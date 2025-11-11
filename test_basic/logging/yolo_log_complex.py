# realtime_yolo_logger.py
import time, csv, sys
import numpy as np
import cv2
from ultralytics import YOLO

# --- Configuration ---
VIDEO_SOURCE = 0               # 0 for webcam, or "udp://192.168.2.1:5600", or filename
MODEL_PATH = "yolo11n.pt"      # your model path / pretrained
OUT_VIDEO = "trial_video.avi"  # optional video save (set None to disable)
OUT_CSV = "detections.csv"
CONF_THRESH = 0.3              # minimum confidence to log/draw
DISPLAY_SCALE = 1.0            # set <1.0 to downscale for speed
FONT = cv2.FONT_HERSHEY_SIMPLEX

# --- Init model & capture ---
model = YOLO(MODEL_PATH)
cap = cv2.VideoCapture(VIDEO_SOURCE)
if not cap.isOpened():
    print("Cannot open video source:", VIDEO_SOURCE); sys.exit(1)

w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH) * DISPLAY_SCALE)
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT) * DISPLAY_SCALE)
fps = cap.get(cv2.CAP_PROP_FPS) or 20.0

video_out = None
if OUT_VIDEO:
    fourcc = cv2.VideoWriter_fourcc(*"XVID")
    video_out = cv2.VideoWriter(OUT_VIDEO, fourcc, fps, (w,h))

# --- CSV writer ---
csv_file = open(OUT_CSV, "w", newline="")
csv_writer = csv.writer(csv_file)
csv_writer.writerow(["ts_ms", "frame_idx", "x", "y", "w", "h", "class_id", "conf"])

frame_idx = 0
print("Starting loop. Press 'q' to quit.")

try:
    while True:
        ret, frame = cap.read()
        if not ret:
            print("End of stream or cannot read frame.")
            break

        # optional scaling
        if DISPLAY_SCALE != 1.0:
            frame = cv2.resize(frame, (w, h))

        ts_ms = int(time.time() * 1000)

        # Ultralyics predict - pass frame directly
        results = model(frame, stream=False, imgsz=640)  # imgsz controls internal resize

        # results could be a list with 1 element; handle both styles
        res = results[0] if isinstance(results, list) and len(results) > 0 else results

        # extract boxes: handle ultralytics vX differences
        boxes_np = []
        # `res.boxes` has attributes xyxy, conf, cls in many versions
        boxes = res.boxes
        xyxy = boxes.xyxy.cpu().numpy()   # Nx4
        confs = boxes.conf.cpu().numpy()  # N
        clss = boxes.cls.cpu().numpy().astype(int)  # N
        for (x1,y1,x2,y2), c, cl in zip(xyxy, confs, clss):
            if c < CONF_THRESH: continue
            x, y, bw, bh = int(x1), int(y1), int(x2-x1), int(y2-y1)
            boxes_np.append((x,y,bw,bh,cl,float(c)))

        # Draw and log
        for (x,y,bw,bh,cl,c) in boxes_np:
            # Rectangle
            color = (0, 200, 0)
            cv2.rectangle(frame, (x,y), (x+bw, y+bh), color, 2)

            # Text: class/conf + bbox coords
            label = f"{cl}:{c:.2f}"
            bboxinfo = f"x={x},y={y},w={bw},h={bh}"
            # place label above box if space, else inside top-left
            txt_pos = (x, y-8) if y-20 > 0 else (x, y+15)
            cv2.putText(frame, label, txt_pos, FONT, 0.5, color, 1, cv2.LINE_AA)

            # small filled rectangle for bboxinfo in top-right of bbox
            info_pos = (x, y + bh + 18) if (y + bh + 30) < h else (x, y + bh - 6)
            cv2.putText(frame, bboxinfo, info_pos, FONT, 0.45, (255,255,255), 1, cv2.LINE_AA)

            # write to CSV: x,y,w,h
            csv_writer.writerow([ts_ms, frame_idx, x, y, bw, bh, cl, f"{c:.4f}"])

        # overlay global info
        cv2.putText(frame, f"Frame:{frame_idx} Time:{ts_ms}", (8,20), FONT, 0.5, (255,255,0), 1, cv2.LINE_AA)

        # show
        cv2.imshow("YOLO live", frame)
        if video_out:
            video_out.write(frame)

        frame_idx += 1
        key = cv2.waitKey(1) & 0xFF
        if key == ord("q"):
            break

finally:
    csv_file.close()
    cap.release()
    if video_out:
        video_out.release()
    cv2.destroyAllWindows()
    print("Done.")

    # After this, run the log_plotting.py to visualize detections from detections.csv