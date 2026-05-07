from ultralytics import YOLO
import os

# Configure the tracking parameters and run the tracker
model_uno_s = YOLO("../../test_advanced/object_detection_model/yolo26s_uno.pt")
model_cou_s = YOLO("../../test_advanced/object_detection_model/yolo26s_cou.pt")
model_walia_s = YOLO("../../test_advanced/object_detection_model/yolo26s_walia.pt")
model_tc_s = YOLO("../../test_advanced/object_detection_model/yolo26s_tc.pt")

model_uno_n = YOLO("../../test_advanced/object_detection_model/yolo26n_uno.pt")
model_cou_n = YOLO("../../test_advanced/object_detection_model/yolo26n_cou.pt")
model_walia_n = YOLO("../../test_advanced/object_detection_model/yolo26n_walia.pt")
model_tc_n = YOLO("../../test_advanced/object_detection_model/yolo26n_tc.pt")

model_uno_s_11 = YOLO("../../test_advanced/object_detection_model/yolo11s_uno.pt")
model_cou_s_11 = YOLO("../../test_advanced/object_detection_model/yolo11s_cou.pt")
model_walia_s_11 = YOLO("../../test_advanced/object_detection_model/yolo11s_walia.pt")
model_tc_s_11 = YOLO("../../test_advanced/object_detection_model/yolo11s_tc.pt")

model_uno_n_11 = YOLO("../../test_advanced/object_detection_model/yolo11n_uno.pt")
model_cou_n_11 = YOLO("../../test_advanced/object_detection_model/yolo11n_cou.pt")
model_walia_n_11 = YOLO("../../test_advanced/object_detection_model/yolo11n_walia.pt")
model_tc_n_11 = YOLO("../../test_advanced/object_detection_model/yolo11n_tc.pt")

model_overfit = YOLO("../../test_advanced/object_detection_model/yolo26s_pepsidtu_v2.pt")

def video_evaluate(source, model, filename):
    results = model.track(
        source=source,
        conf=0.5,
        iou=0.5,
        show=True,
        stream=True,
        persist=True,
        verbose=True  # Prints FPS stats
    )

    os.makedirs(os.path.dirname(filename), exist_ok=True)

    with open(filename, "w") as f:
        for frame_id, result in enumerate(results, start=1):
            if result.boxes is None or result.boxes.id is None:
                continue

            boxes = result.boxes.xyxy.cpu().numpy()
            ids = result.boxes.id.int().cpu().tolist()
            confs = result.boxes.conf.cpu().tolist()
            classes = result.boxes.cls.int().cpu().tolist()

            for box, track_id, conf, classes in zip(boxes, ids, confs, classes):
                x1, y1, x2, y2 = box
                w = x2 - x1
                h = y2 - y1

                f.write(f"{frame_id},{track_id},{x1},{y1},{w},{h},{conf},1,{int(classes)},-1\n")

def eval(name):
    filename = f"video/mot_{name}.mp4"
    video_evaluate(filename, model_overfit, f"mot_eval/overfit/data/mot_{name}.txt")
    video_evaluate(filename, model_uno_n, f"mot_eval/uno_n/data/mot_{name}.txt")
    video_evaluate(filename, model_uno_s, f"mot_eval/uno_s/data/mot_{name}.txt")
    video_evaluate(filename, model_cou_n, f"mot_eval/cou_n/data/mot_{name}.txt")
    video_evaluate(filename, model_cou_s, f"mot_eval/cou_s/data/mot_{name}.txt")
    video_evaluate(filename, model_walia_n, f"mot_eval/walia_n/data/mot_{name}.txt")
    video_evaluate(filename, model_walia_s, f"mot_eval/walia_s/data/mot_{name}.txt")
    video_evaluate(filename, model_tc_n, f"mot_eval/tc_n/data/mot_{name}.txt")
    video_evaluate(filename, model_tc_s, f"mot_eval/tc_s/data/mot_{name}.txt")

    video_evaluate(filename, model_uno_n_11, f"mot_eval/uno_n_11/data/mot_{name}.txt")
    video_evaluate(filename, model_uno_s_11, f"mot_eval/uno_s_11/data/mot_{name}.txt")
    video_evaluate(filename, model_cou_n_11, f"mot_eval/cou_n_11/data/mot_{name}.txt")
    video_evaluate(filename, model_cou_s_11, f"mot_eval/cou_s_11/data/mot_{name}.txt")
    video_evaluate(filename, model_walia_n_11, f"mot_eval/walia_n_11/data/mot_{name}.txt")
    video_evaluate(filename, model_walia_s_11, f"mot_eval/walia_s_11/data/mot_{name}.txt")
    video_evaluate(filename, model_tc_n_11, f"mot_eval/tc_n_11/data/mot_{name}.txt")
    video_evaluate(filename, model_tc_s_11, f"mot_eval/tc_s_11/data/mot_{name}.txt")

if __name__ == "__main__":
    
    eval("center_descend")
    eval("center_forward_2")
    eval("center_yaw")
    eval("east_forward")
    eval("north_forward")
    eval("north_yaw")
    eval("northeast_forward")
    eval("northwest_forward")
    eval("south_forward")
    #eval("south_yaw")
    eval("south_yaw_2")
    eval("southeast_forward")
    #eval("southeast_yawascend")
    eval("southeast_yawascend_2")
    eval("southwest_forward")
    #eval("southwest_yawascend")
    eval("southwest_yawascend_2")
    eval("west_forward")




