def get_model_path(modelOpt):
    match modelOpt["dataset"]:
        case "COU":
            match modelOpt["which_model"]:
                case "yolo11n":
                    model_path = "object_detection_model/yolo11n_cou.pt"
                case "yolo11s":
                    model_path = "object_detection_model/yolo11s_cou.pt"
                case "yolo26n":
                    model_path = "object_detection_model/yolo26n_cou.pt"
                case "yolo26s":
                    model_path = "object_detection_model/yolo26s_cou.pt"
        case "COCO":
            match modelOpt["which_model"]:
                case "yolo11n":
                    model_path = "object_detection_model/yolo11n.pt"
                case "yolo11s":
                    model_path = "object_detection_model/yolo11s.pt"
                case "yolo26n":
                    model_path = "object_detection_model/yolo26n.pt"
                case "yolo26s":
                    model_path = "object_detection_model/yolo26s.pt"
        case "TrashCan":
            match modelOpt["which_model"]:
                case "yolo11n":
                    model_path = "object_detection_model/yolo11n_tc.pt"
                case "yolo11s":
                    model_path = "object_detection_model/yolo11s_tc.pt"
                case "yolo26n":
                    model_path = "object_detection_model/yolo26n_tc.pt"
                case "yolo26s":
                    model_path = "object_detection_model/yolo26s_tc.pt"
        case "Pepsi_DTU":
            match modelOpt["which_model"]:
                case "yolo26n":
                    #model = YOLO("object_detection_model/yolo26n_pepsidtu.pt")
                    model_path = "object_detection_model/yolo26n_pepsidtu_v2.pt"
                case "yolo26s":
                    #model = YOLO("object_detection_model/yolo26s_pepsidtu.pt")
                    model_path  = "object_detection_model/yolo26s_pepsidtu_v2.pt"
        case "Pepsi_DTU_Rotate":
            match modelOpt["which_model"]:
                case "yolo26n":
                    model_path = "object_detection_model/yolo26n_pepsidtu_rotate.pt"
                case "yolo26s":
                    model_path = "object_detection_model/yolo26s_pepsidtu_rotate.pt"
        case "UNO":
            match modelOpt["which_model"]:
                case "yolo11n":
                    model_path = "object_detection_model/yolo11n_uno.pt"
                case "yolo11s":
                    model_path = "object_detection_model/yolo11s_uno.pt"
                case "yolo26n":
                    model_path = "object_detection_model/yolo26n_uno.pt"
                case "yolo26s":
                    model_path = "object_detection_model/yolo26s_uno.pt"
        case "Venise":
            match modelOpt["which_model"]:
                case "yolo26n":
                    model_path = "object_detection_model/yolo26n_venise.pt"
                case "yolo26s":
                    model_path = "object_detection_model/yolo26s_venise.pt"
        case "Morgane":
            match modelOpt["which_model"]:
                case "yolo26n":
                    model_path = "object_detection_model/yolo26n_morgane.pt"
                case "yolo26s":
                    model_path = "object_detection_model/yolo26s_morgane.pt"
        case "Walia":
            match modelOpt["which_model"]:
                case "yolo11n":
                    model_path = "object_detection_model/yolo11n_walia.pt"
                case "yolo11s":
                    model_path = "object_detection_model/yolo11s_walia.pt"
                case "yolo26n":
                    model_path = "object_detection_model/yolo26n_walia.pt"
                case "yolo26s":
                    model_path = "object_detection_model/yolo26s_walia.pt"
    return model_path