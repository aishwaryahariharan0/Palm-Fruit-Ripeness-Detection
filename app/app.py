import os
import cv2
import pyodbc
import threading
import webbrowser
from datetime import datetime
from flask import Flask, render_template, request, send_from_directory, url_for
from ultralytics import YOLO
from werkzeug.utils import secure_filename

# ---------------- PATHS ----------------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
RESULT_FOLDER = os.path.join(BASE_DIR, "static", "results")

os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs(RESULT_FOLDER, exist_ok=True)

# ---------------- APP ----------------
app = Flask(__name__)
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER
app.config["MAX_CONTENT_LENGTH"] = 500 * 1024 * 1024  # 500 MB max upload

# ---------------- YOLO MODEL ----------------
model = YOLO("best.pt")

# ---------------- ALLOWED EXTENSIONS ----------------
IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}
VIDEO_EXTENSIONS = {".mp4", ".avi", ".mov", ".mkv"}

# ---------------- DATABASE CONNECTION ----------------
def get_db_connection():
    conn = pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=localhost;"         # Change to your SQL Server name/IP
        "DATABASE=palm_project;"
        "Trusted_Connection=yes;"   # Windows Authentication
        # If using SQL login, replace above line with:
        # "UID=your_username;PWD=your_password;"
    )
    return conn

# ---------------- SAVE TO DATABASE ----------------
def save_to_db(image_path, label, confidence, file_type):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO dbo.predictions (image_path, label, confidence, created_at, file_type) "
            "VALUES (?, ?, ?, ?, ?)",
            (image_path, label, confidence, datetime.now(), file_type)
        )
        conn.commit()
        conn.close()
    except Exception as e:
        print(f"[DB ERROR] {e}")

# ---------------- PROCESS IMAGE ----------------
def process_image(file_path, filename):
    results = model(file_path, conf=0.25)
    result = results[0]

    detections = result.boxes
    annotated = result.plot()

    # Save annotated image
    result_path = os.path.join(RESULT_FOLDER, filename)
    cv2.imwrite(result_path, annotated)

    if detections is None or len(detections) == 0:
        return {
            "detected": False,
            "message": "The given image is not a palm fruit.",
            "label": "No fruit",
            "confidence": 0.0,
            "filename": filename,
        }

    # Pick the detection with highest confidence
    best_idx = detections.conf.argmax().item()
    best_conf = float(detections.conf[best_idx]) * 100
    best_cls = int(detections.cls[best_idx])
    label = result.names[best_cls]

    message = (
        f"The uploaded image is a palm fruit. "
        f"The fruit is {label.upper()} with {best_conf:.1f}% confidence."
    )

    return {
        "detected": True,
        "message": message,
        "label": label,
        "confidence": round(best_conf, 1),
        "filename": filename,
    }

# ---------------- PROCESS VIDEO ----------------
def process_video(file_path, filename, stride=10):
    cap = cv2.VideoCapture(file_path)
    if not cap.isOpened():
        return {"error": "Cannot open video file."}

    # Output video setup
    out_filename = "processed_" + filename
    # Use .mp4 extension for output always (widely supported)
    out_filename = os.path.splitext(out_filename)[0] + ".mp4"
    out_path = os.path.join(RESULT_FOLDER, out_filename)

    fps = cap.get(cv2.CAP_PROP_FPS) or 25
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    # Try H.264 first (browser-compatible). Fall back to mp4v if unavailable.
    fourcc = cv2.VideoWriter_fourcc(*"avc1")
    out = cv2.VideoWriter(out_path, fourcc, fps, (width, height))
    if not out.isOpened():
        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        out = cv2.VideoWriter(out_path, fourcc, fps, (width, height))

    frame_id = 0
    sampled_count = 0          # how many frames were actually sampled
    last_annotated = None

    label_counts = {}
    conf_sum = 0.0
    detected_frames = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_id % stride == 0:
            sampled_count += 1
            results = model(frame, conf=0.25)
            result = results[0]
            last_annotated = result.plot()

            if result.boxes is not None and len(result.boxes) > 0:
                detected_frames += 1
                best_idx = result.boxes.conf.argmax().item()
                best_conf = float(result.boxes.conf[best_idx])
                best_cls = int(result.boxes.cls[best_idx])
                lbl = result.names[best_cls]
                label_counts[lbl] = label_counts.get(lbl, 0) + 1
                conf_sum += best_conf

        if last_annotated is not None:
            out.write(last_annotated)
        else:
            out.write(frame)

        frame_id += 1

    cap.release()
    out.release()

    total_checked = max(sampled_count, 1)

    if detected_frames == 0:
        return {
            "detected": False,
            "message": "The given video does not contain palm fruit.",
            "label": "No fruit",
            "confidence": 0.0,
            "out_filename": out_filename,
        }

    # Dominant label
    dominant_label = max(label_counts, key=label_counts.get)
    avg_conf = (conf_sum / detected_frames) * 100
    overall_pct = (detected_frames / total_checked) * 100

    message = (
        f"In this video, palm fruit is detected and it is "
        f"{dominant_label.upper()} with overall confidence {avg_conf:.1f}%. "
        f"({overall_pct:.0f}% of sampled frames contained palm fruit.)"
    )

    return {
        "detected": True,
        "message": message,
        "label": dominant_label,
        "confidence": round(avg_conf, 1),
        "out_filename": out_filename,
    }

# ---------------- ROUTES ----------------
@app.route("/", methods=["GET", "POST"])
def index():
    error = None

    if request.method == "POST":
        file = request.files.get("file")
        if not file or file.filename == "":
            error = "No file selected. Please choose a file."
            return render_template("index.html", error=error)

        filename = secure_filename(file.filename)
        ext = os.path.splitext(filename)[1].lower()

        if ext not in IMAGE_EXTENSIONS and ext not in VIDEO_EXTENSIONS:
            error = f"Unsupported file type '{ext}'. Please upload JPG, PNG, WEBP, MP4, AVI, MOV, or MKV."
            return render_template("index.html", error=error)

        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)

        # ---------- IMAGE ----------
        if ext in IMAGE_EXTENSIONS:
            info = process_image(file_path, filename)
            save_to_db(filename, info["label"], info["confidence"], "image")
            return render_template("image_result.html", **info)

        # ---------- VIDEO ----------
        info = process_video(file_path, filename)
        if "error" in info:
            return render_template("index.html", error=info["error"])
        save_to_db(filename, info["label"], info["confidence"], "video")
        return render_template("video_result.html", **info)

    return render_template("index.html", error=error)


@app.route("/download/<path:filename>")
def download_file(filename):
    return send_from_directory(RESULT_FOLDER, filename, as_attachment=True)


# ---------------- RUN ----------------
if __name__ == "__main__":
    # Auto-open browser after 1 second
    threading.Timer(1.0, lambda: webbrowser.open("http://127.0.0.1:5000")).start()
    app.run(debug=True)
