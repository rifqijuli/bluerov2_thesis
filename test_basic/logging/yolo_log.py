import csv, time
from ultralytics import YOLO
import cv2

model = YOLO("yolo11n.pt")
out_csv = "detections.csv"
cap = cv2.VideoCapture(0)   # or video stream

with open(out_csv, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["ts_ms","frame","bbox_x","bbox_y","bbox_w","bbox_h","class_id","conf"])
    frame_idx = 0
    while True:
        ret, frame = cap.read()
        if not ret: break
        ts_ms = int(time.time()*1000)
        results = model(frame)    # single image inference
        # results[0].boxes.xywhn or .boxes.xyxy depending on version
        boxes = results[0].boxes.xyxy.cpu().numpy() if hasattr(results[0].boxes, "xyxy") else []
        confs = results[0].boxes.conf.cpu().numpy() if hasattr(results[0].boxes, "conf") else []
        cls = results[0].boxes.cls.cpu().numpy() if hasattr(results[0].boxes, "cls") else []
        for (x1,y1,x2,y2), c, cl in zip(boxes, confs, cls):
            w = x2-x1; h = y2-y1
            writer.writerow([ts_ms, frame_idx, int(x1), int(y1), int(w), int(h), int(cl), float(c)])
        frame_idx += 1