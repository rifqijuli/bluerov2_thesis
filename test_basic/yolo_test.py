from ultralytics import YOLO

model = YOLO('yolo11n.pt')  # load a pretrained YOLOv8n model

results = model.predict(source='https://ultralytics.com/images/bus.jpg', conf=0.25, save=True)  # predict on an image
# results = model.track(source='0', conf=0.25, save=True)

for r in results:
    r.show()  # display results