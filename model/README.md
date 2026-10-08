# YOLOv8 Model Documentation

## Overview

This project uses a custom-trained **YOLOv8 object detection model** to detect palm fruits and classify them according to their ripeness level.

The trained model is integrated into a Flask-based web application and is used for both image and video detection.

The model identifies palm fruits, predicts their ripeness class, and provides a confidence score for each detection.

---

## Model Purpose

The main purpose of the model is to:

- Detect palm fruits in images.
- Detect palm fruits in video frames.
- Classify detected fruits according to their ripeness stage.
- Generate bounding boxes around detected fruits.
- Calculate a confidence score for each prediction.
- Provide detection results to the Flask web application.

---

## Model Architecture

The project uses **YOLOv8 (You Only Look Once version 8)** through the **Ultralytics** framework.

YOLOv8 is an object detection model designed to identify objects and their locations within images or video frames.

For this project, the model was custom-trained using an annotated palm fruit dataset for ripeness detection.

---

## Ripeness Classes

The final trained model uses the following three classes:

| Class | Description |
|---|---|
| **Ripe** | Palm fruit identified as ripe |
| **Semi-Ripe** | Palm fruit identified as partially ripe |
| **Unripe** | Palm fruit identified as unripe |

The class names are defined by the trained model configuration and are used by the application when displaying detection results.

---

## Model Input

The model receives image data processed by the application.

Supported application inputs include:

- Uploaded images
- Uploaded videos

For video detection, the application processes the video frame by frame and sends the required frames to the YOLOv8 model for detection.

---

## Model Output

For every detected palm fruit, the model provides:

- **Bounding box** – location of the detected fruit.
- **Class label** – predicted ripeness category.
- **Confidence score** – model confidence for the prediction.

A typical detection can be represented as:

```text
Detected Object
    ├── Class: Ripe
    ├── Confidence: 0.xx
    └── Bounding Box: (x1, y1, x2, y2)
```

The actual confidence value depends on the input image or video frame.

---

## Dataset

The model was trained using an annotated palm fruit dataset.

The dataset contains palm fruit images representing different ripeness stages. Each training image was prepared with object-detection annotations containing bounding boxes and corresponding class labels.

Additional non-palm fruit images were also included during dataset preparation to help the detection system distinguish palm fruits from other visually different objects.

The complete dataset is **not included in this public repository**.

---

## Training Process

The general model development process was:

```text
Palm Fruit Image Collection
          ↓
Image Annotation
          ↓
Dataset Preparation
          ↓
YOLO-Compatible Dataset
          ↓
YOLOv8 Model Training
          ↓
Model Validation
          ↓
Trained Model Weights
          ↓
Flask Application Integration
```

The trained model was selected for integration into the final web application.

---

## Model Integration

The trained YOLOv8 model is loaded by the Flask application using the **Ultralytics** Python library.

The application uses the model to process uploaded images and video frames.

The overall integration flow is:

```text
User Upload
     ↓
Flask Application
     ↓
Image / Video Processing
     ↓
YOLOv8 Model
     ↓
Palm Fruit Detection
     ↓
Ripeness Classification
     ↓
Bounding Box + Confidence Score
     ↓
Result Display
```

---

## Image Detection

For image input, the application sends the uploaded image to the YOLOv8 model.

The model detects palm fruits and predicts their corresponding ripeness classes.

The resulting image is displayed with:

- Bounding boxes
- Ripeness labels
- Confidence scores

---

## Video Detection

For video input, the application uses OpenCV to read the video frames.

Each processed frame is passed through the YOLOv8 model.

The detection results are drawn on the frames before they are combined into the processed output video.

```text
Input Video
    ↓
Frame Extraction
    ↓
YOLOv8 Detection
    ↓
Ripeness Classification
    ↓
Bounding Box + Confidence
    ↓
Processed Frame
    ↓
Output Video
```

---

## Model Weights

The trained YOLOv8 model weights are **not included in this public repository**.

This is intentional because trained model weights can be relatively large and may expose the complete trained model.

The public repository therefore contains documentation about the model rather than the private weight file itself.

The application requires the appropriate trained model weights to perform actual detection.

---

## Local Model Setup

If the trained model weights are available locally, configure the application so that the model path points to the trained `.pt` file.

For example:

```python
from ultralytics import YOLO

model = YOLO("path/to/best.pt")
```

The exact model path depends on the local project configuration.

Do not commit private model weights to the public repository unless you intentionally decide to distribute them.

---

## Model Usage in the Application

The model is used as the detection component of the complete system.

The application combines:

- **YOLOv8** for object detection
- **OpenCV** for image and video processing
- **Flask** for the web interface and backend
- **Microsoft SQL Server** for prediction storage

This creates an end-to-end palm fruit ripeness detection system.

---

## Performance Considerations

Detection performance can vary depending on:

- Image resolution
- Lighting conditions
- Camera angle
- Fruit size
- Background complexity
- Partial occlusion
- Image quality
- Similar-looking objects

The model performs best on inputs that are reasonably similar to the conditions represented in the training dataset.

---

## Limitations

- Very small fruits may be difficult to detect.
- Partially hidden fruits may reduce detection reliability.
- Poor lighting can affect detection performance.
- Blurred video frames may affect predictions.
- Model performance depends on the quality and diversity of the training dataset.
- Further testing with larger real-world datasets is recommended before production deployment.

---

## Repository Scope

The public repository includes this model documentation so that users can understand the role of the YOLOv8 model within the project.

The following model-related items are intentionally excluded:

- Complete training dataset
- Training runs
- Experiment outputs
- Private model weights
- Local training environment
- Other temporary training files

---

## Note

This model documentation is provided for academic, learning, and project demonstration purposes.

The YOLOv8 model is a custom-trained component of the Palm Fruit Ripeness Detection application and should be further validated with diverse real-world data before being used in production agricultural environments.
