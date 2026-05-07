from ultralytics import YOLO

# Load an official or custom model
model = YOLO("../../test_advanced/object_detection_model/yolo26s_pepsidtu_v2.pt")  # Load a custom-trained model

# Perform tracking with the model
results = model.track("video/mot_west_forward.mp4", show=True)  # Tracking with default tracker