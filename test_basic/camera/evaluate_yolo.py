from ultralytics import YOLO
import os
import csv

# Configure the tracking parameters and run the tracker
model_uno_s = YOLO("../../test_advanced/object_detection_model/yolo26s_uno.pt")
model_cou_s = YOLO("../../test_advanced/object_detection_model/yolo26s_cou.pt")
model_walia_s = YOLO("../../test_advanced/object_detection_model/yolo26s_walia.pt")
model_tc_s = YOLO("../../test_advanced/object_detection_model/yolo26s_tc.pt")
model_sd35_s = YOLO("../../test_advanced/object_detection_model/yolo26s_sd35.pt")

model_uno_n = YOLO("../../test_advanced/object_detection_model/yolo26n_uno.pt")
model_cou_n = YOLO("../../test_advanced/object_detection_model/yolo26n_cou.pt")
model_walia_n = YOLO("../../test_advanced/object_detection_model/yolo26n_walia.pt")
model_tc_n = YOLO("../../test_advanced/object_detection_model/yolo26n_tc.pt")
model_sd35_n = YOLO("../../test_advanced/object_detection_model/yolo26n_sd35.pt")

model_uno_s_11 = YOLO("../../test_advanced/object_detection_model/yolo11s_uno.pt")
model_cou_s_11 = YOLO("../../test_advanced/object_detection_model/yolo11s_cou.pt")
model_walia_s_11 = YOLO("../../test_advanced/object_detection_model/yolo11s_walia.pt")
model_tc_s_11 = YOLO("../../test_advanced/object_detection_model/yolo11s_tc.pt")
model_sd35_s_11 = YOLO("../../test_advanced/object_detection_model/yolo11s_sd35.pt")

model_uno_n_11 = YOLO("../../test_advanced/object_detection_model/yolo11n_uno.pt")
model_cou_n_11 = YOLO("../../test_advanced/object_detection_model/yolo11n_cou.pt")
model_walia_n_11 = YOLO("../../test_advanced/object_detection_model/yolo11n_walia.pt")
model_tc_n_11 = YOLO("../../test_advanced/object_detection_model/yolo11n_tc.pt")
model_sd35_n_11 = YOLO("../../test_advanced/object_detection_model/yolo11n_sd35.pt")

model_overfit = YOLO("../../test_advanced/object_detection_model/yolo26s_pepsidtu_v2.pt")

CSV_PATH = "results_yolo_eval_thesis.csv"
CSV_FIELDS = ["sequence", "model", "mAP50", "mAP50-95", "precision", "recall"]

# Write header once at startup
os.makedirs("val_eval", exist_ok=True)
if not os.path.exists(CSV_PATH):
    with open(CSV_PATH, "w", newline="") as f:
        csv.DictWriter(f, fieldnames=CSV_FIELDS).writeheader()

def video_evaluate(model, filename, seq_name, model_name):
    metrics = model.val(
        data=filename,
        split="test",
        conf=0.5,
        iou=0.5,
        project="thesis_evaluation_yolo",
        name=f"{seq_name}/{model_name}",
        exist_ok=True,
    )
    row = {
        "sequence":  seq_name,
        "model":     model_name,
        "mAP50":     round(metrics.box.map50, 4),
        "mAP50-95":  round(metrics.box.map,   4),
        "precision": round(metrics.box.mp,    4),
        "recall":    round(metrics.box.mr,    4),
    }
    with open(CSV_PATH, "a", newline="") as f:  # ← "a" = append
        csv.DictWriter(f, fieldnames=CSV_FIELDS).writerow(row)
    print(f"✓ Written: {seq_name} / {model_name}")

def eval(name, model):
    filename = os.path.expanduser(f"~/Downloads/Hasil/{name}/data.yaml")

    match model:
        case "cou":
            video_evaluate(model_cou_n, filename, name, "cou_n_26")
            video_evaluate(model_cou_s, filename, name, "cou_s_26")
            video_evaluate(model_cou_n_11, filename, name, "cou_n_11")
            video_evaluate(model_cou_s_11, filename, name, "cou_s_11")
        case "tc":    
            video_evaluate(model_tc_n, filename, name, "tc_n_26")
            video_evaluate(model_tc_s, filename, name, "tc_s_26")
            video_evaluate(model_tc_n_11, filename, name, "tc_n_11")
            video_evaluate(model_tc_s_11, filename, name, "tc_s_11")
        case "uno":
            video_evaluate(model_uno_n, filename, name, "uno_n_26")
            video_evaluate(model_uno_s, filename, name, "uno_s_26")
            video_evaluate(model_uno_n_11, filename, name, "uno_n_11")
            video_evaluate(model_uno_s_11, filename, name, "uno_s_11")
        case "walia":
            video_evaluate(model_walia_n, filename, name, "walia_n_26")
            video_evaluate(model_walia_s, filename, name, "walia_s_26")
            video_evaluate(model_walia_n_11, filename, name, "walia_n_11")
            video_evaluate(model_walia_s_11, filename, name, "walia_s_11")
        case "sd35":
            video_evaluate(model_sd35_n, filename, name, "sd35_n_26")
            video_evaluate(model_sd35_s, filename, name, "sd35_s_26")
            video_evaluate(model_sd35_n_11, filename, name, "sd35_n_11")
            video_evaluate(model_sd35_s_11, filename, name, "sd35_s_11")
        case "overfit":
            video_evaluate(model_overfit, filename, name, "overfit_s_26")


if __name__ == "__main__":

    #eval('combined', "cou")
    #eval('combined', "tc")
    #eval('combined', "uno")
    #eval('combined', "walia")
    #eval('combined', "overfit")
    eval('combined', "sd35")