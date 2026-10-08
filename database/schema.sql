-- ============================================================
-- Palm Fruit Ripeness Detection
-- MySQL Database Schema
-- File: schema.sql
-- ============================================================

-- Create database
CREATE DATABASE IF NOT EXISTS palm_project
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE palm_project;

-- ============================================================
-- Table: predictions
-- Stores every uploaded image/video and its prediction details.
-- One row = one uploaded file / prediction record.
-- ============================================================

CREATE TABLE IF NOT EXISTS predictions (
    id BIGINT UNSIGNED NOT NULL AUTO_INCREMENT,

    -- Unique reference number for each uploaded record
    unique_number VARCHAR(50) NOT NULL,

    -- Original uploaded file name
    file_name VARCHAR(255) NOT NULL,

    -- Type of uploaded file: image or video
    file_type ENUM('image', 'video') NOT NULL,

    -- Directory/path where the uploaded file is stored
    file_directory VARCHAR(500) NOT NULL,

    -- Prediction output
    prediction VARCHAR(50) NOT NULL,

    -- Model confidence score (for example: 0.9523 = 95.23%)
    confidence DECIMAL(6,4) NULL,

    -- Date on which the file was uploaded
    uploaded_date DATE NOT NULL,

    -- Time at which the file was uploaded
    uploaded_time TIME NOT NULL,

    -- Date and time when the database record was created
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,

    PRIMARY KEY (id),

    -- Each uploaded record must have a unique reference number
    UNIQUE KEY uq_predictions_unique_number (unique_number),

    -- Useful indexes for searching/filtering records
    INDEX idx_uploaded_date (uploaded_date),
    INDEX idx_prediction (prediction),
    INDEX idx_file_type (file_type)
)
ENGINE=InnoDB
DEFAULT CHARACTER SET=utf8mb4
COLLATE=utf8mb4_unicode_ci;


-- ============================================================
-- INSERT EXAMPLES
-- ============================================================
-- The application should generate unique_number, file_directory,
-- uploaded_date and uploaded_time from the user's upload event.
--
-- Example for an image upload:
--
-- INSERT INTO predictions
-- (
--     unique_number,
--     file_name,
--     file_type,
--     file_directory,
--     prediction,
--     confidence,
--     uploaded_date,
--     uploaded_time
-- )
-- VALUES
-- (
--     'PFR-20261007-000001',
--     'palm_image_001.jpg',
--     'image',
--     'static/results/PFR-20261007-000001/palm_image_001.jpg',
--     'Ripe',
--     0.9523,
--     CURDATE(),
--     CURTIME()
-- );


-- ============================================================
-- INSERT EXAMPLE FOR VIDEO
-- ============================================================
--
-- INSERT INTO predictions
-- (
--     unique_number,
--     file_name,
--     file_type,
--     file_directory,
--     prediction,
--     confidence,
--     uploaded_date,
--     uploaded_time
-- )
-- VALUES
-- (
--     'PFR-20261007-000002',
--     'palm_video_001.mp4',
--     'video',
--     'static/results/PFR-20261007-000002/palm_video_001.mp4',
--     'Semi-Ripe',
--     0.8735,
--     CURDATE(),
--     CURTIME()
-- );


-- ============================================================
-- BASIC RETRIEVAL QUERIES
-- ============================================================

-- Get all prediction records
-- SELECT * FROM predictions ORDER BY id DESC;

-- Get the latest uploaded record
-- SELECT * FROM predictions ORDER BY uploaded_date DESC, uploaded_time DESC LIMIT 1;

-- Find a record using its unique number
-- SELECT * FROM predictions
-- WHERE unique_number = 'PFR-20261007-000001';

-- Get all Ripe predictions
-- SELECT * FROM predictions
-- WHERE prediction = 'Ripe'
-- ORDER BY uploaded_date DESC, uploaded_time DESC;

-- Get records uploaded on the current date
-- SELECT * FROM predictions
-- WHERE uploaded_date = CURDATE()
-- ORDER BY uploaded_time DESC;
