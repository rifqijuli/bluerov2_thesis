from ultralytics import YOLO

# Load an official or custom model
model = YOLO('../../yolo26n_pepsidtu.pt')  # Load a custom-trained model

# Perform tracking with the model
results = model.track('../../test4.mkv', show=True)  # Tracking with default tracker