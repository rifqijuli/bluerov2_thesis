import torch
import torch.nn as nn
import torchvision.transforms as T
import numpy as np
import cv2
import gi
from camera import rov_camera
from ultralytics import YOLO
import string
from tracking import yolo_track
from collections import defaultdict
from image_enhancement import funie

from image_enhancement.nets.funiegan import GeneratorFunieGAN as Generator  # adjust import path to match your repo

# mouse callback function
def get_click(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        print(f"Clicked coordinates: X={x}, Y={y}")
        click_mouse_position.set_position(x, y)

#!/usr/bin/env python

#if __name__ == '__main__':
def image_main(cameraOpt = False, modelOpt = False):


    """
    BlueRov video capture class
    """

    class cameraOpt:
        isROVCamera = False  # Set to True to use ROV camera, False for local webcam    

    class modelOpt:
        isCOU = False # Set to True if uses CoU dataset

    # Load the YOLO11 model
    if modelOpt.isCOU:
        model = YOLO("object_detection_model/yolo11n_cou.pt")
    else:
        model = YOLO("object_detection_model/yolo11n.pt")

    # FUnIE-GAN
    # --- Load pretrained FUnIE-GAN model ---
    device = "cuda" if torch.cuda.is_available() else "cpu"
    model_path = "image_enhancement/funie_generator.pth"  # change if different
    G = Generator().to(device)
    G.load_state_dict(torch.load(model_path, map_location=device))
    G.eval()

    # --- Define transforms ---
    to_tensor = T.Compose([
        T.ToPILImage(),
        T.Resize((256, 256)),
        T.ToTensor()
    ])
    #OR.. Still cant remove this funie gan to other files
    #img_enhance = funie.funie()

    #ROI image
    class roi_image:
        def __init__(self, x, y, width, height):
            self.x = x
            self.y = y
            self.width = width
            self.height = height

    # Target frame size
    class frameSize:
        def __init__(self, width, height):
            self.width = width
            self.height = height
        
        def center(self):
            return (self.width/2, self.height/2)

    # State management
    class State:
        def __init__(self):
            self.roi_selected = False
            self.object_selected = False
        
        def toggle_roi(self):
            self.roi_selected = not self.roi_selected
        
        def toggle_object(self):
            self.object_selected = not self.object_selected

    #Target object
    class target_object:
        target_status = False
        target_id = -1
        target_class = -1

        def set_target(selected_id, selected_class):
            target_object.target_id = selected_id
            target_object.target_class = selected_class
        
        def toggle_target():
            target_object.target_status = not target_object.target_status


    #Mouse Position
    class click_mouse_position:
        x = 0
        y = 0

        def set_position(x_pos, y_pos):
            click_mouse_position.x = x_pos
            click_mouse_position.y = y_pos
        
        def is_within_object(object):
            print(f"Object coords and size: X={object['x_coord']}, Y={object['y_coord']}, Width={object['width']}, Height={object['height']}")
            print(f"Mouse Poisition: X={click_mouse_position.x}, Y={click_mouse_position.y}")
            if (click_mouse_position.x >= object['x_coord'] and click_mouse_position.x <= object['x_coord'] + object['width'] and
                click_mouse_position.y >= object['y_coord'] and click_mouse_position.y <= object['y_coord'] + object['height']):
                target_object.set_target(object['track_id'], object['obj_class'])
                target_object.toggle_target()
                if system_state.roi_selected is True:
                    system_state.toggle_roi()
                return ( object['track_id'])
            else:
                return False
        
        def reset():
            click_mouse_position.x = 0
            click_mouse_position.y = 0


    print('Initialising stream...')
    print('Press q to quit\nPress s to select ROI\nPress e to remove ROI')
    waited = 0
    system_state = State()

     # Create the video object
    if cameraOpt.isROVCamera:
        video = rov_camera.Video()
        # Add port= if is necessary to use a different one
        while not video.frame_available():
            waited += 1
            print('\r  Frame not available (x{})'.format(waited), end='')
            cv2.waitKey(30)
        print('\nSuccess!\nStarting streaming - press "q" to quit.')
    else:
        video = cv2.VideoCapture(0)

    # YOLO Store the track history
    track_history = defaultdict(lambda: []) 

    # Initiate resize frame size
    targetFrame = frameSize(640, 480)

    while True:
        if cameraOpt.isROVCamera:
            if video.frame_available():
                # Only retrieve and display a frame if it's new
                frame = video.frame()
        else:
            ret, frame = video.read()
            if not ret:
                print("Can't receive frame (stream end?). Exiting ...")
                break  
        # Wait for the next frame to become available
        
        frame = cv2.resize(frame, (targetFrame.width, targetFrame.height))

        try: #If ROI selected
            if target_object.target_status is True:
                results = model.track(frame, persist=True,conf=0.6, iou=0.3, classes=target_object.target_class)
                annotated_frame = results[0].plot()
                track_objects = yolo_track.draw_tracker(results[0], track_history, frame, target_id=target_object.target_id)
                frame = track_objects[0]['frame']

            if system_state.roi_selected:
                rect_img = frame[int(roi_obj.y):int(roi_obj.y+roi_obj.height), int(roi_obj.x):int(roi_obj.x+roi_obj.width)]
                # Do process to the selected image here
                # Convert frame (BGR->RGB)
                rgb = cv2.cvtColor(rect_img, cv2.COLOR_BGR2RGB)
                inp = to_tensor(rgb).unsqueeze(0).to(device)
                
                # Run enhancement
                with torch.no_grad():
                    out = G(inp)
                
                # Convert back to OpenCV format
                out_np = out.squeeze(0).cpu().permute(1, 2, 0).numpy()
                out_np = np.clip(out_np * 255, 0, 255).astype(np.uint8)
                out_bgr = cv2.cvtColor(out_np, cv2.COLOR_RGB2BGR)
                out_bgr = cv2.resize(out_bgr, (int(roi_obj.width), int(roi_obj.height)))
                
                # Change out_bgr to frame if want to track with normal video feed
                try:
                    results = model.track(rect_img, persist=True,conf=0.6, iou=0.3)
                    #results_2 = model.track(out_bgr, persist=True,conf=0.6, iou=0.3)
                    #results = model.track(source="https://youtu.be/LNwODJXcvt4", conf=0.3, iou=0.5, show=True)
                    annotated_frame = results[0].plot()
                    #annotated_frame_2 = results_2[0].plot()
                    track_objects = yolo_track.draw_tracker(results[0], track_history, frame, roi_obj)

                except Exception as e:
                    print(f"No object detection in the frame")
                    annotated_frame_original = rect_img
                
                #Put it back to frame
                frame[int(roi_obj.y):int(roi_obj.y+roi_obj.height), int(roi_obj.x):int(roi_obj.x+roi_obj.width)] = annotated_frame
                cv2.rectangle(frame, 
                    (int(roi_obj.x), int(roi_obj.y)), 
                    (int(roi_obj.x + roi_obj.width), int(roi_obj.y + roi_obj.height)),
                    (0, 255, 255), 2)
                
                #cv2.imshow('rect_img', annotated_frame_2)
                #cv2.imshow('resct_img', track_objects[0]['frame'])
        except:
            pass
        finally:
            # Show both
            cv2.namedWindow('Original')
            cv2.circle(frame, center=(int(targetFrame.center()[0]), int(targetFrame.center()[1])), radius=5, color=(0, 255, 255), thickness=-1)
            cv2.imshow("Original", frame)
            if system_state.roi_selected:
                cv2.setMouseCallback('Original', get_click)
                try:
                    for each in track_objects:
                        if target_object.target_status is False:
                            isInObject = click_mouse_position.is_within_object(each['detected_object'])
                            print(f"Is within object: {isInObject}")
                except:
                    print("No object")
            click_mouse_position.reset()
            # Allow frame to display, and check if user wants to quit
            key = cv2.waitKey(100)
            if key == ord('q'):
                break
            elif key == ord('s'):
                showCrosshair = False
                fromCenter = False
                selected_roi = cv2.selectROI("Select ROI", frame, fromCenter, showCrosshair)
                roi_obj = roi_image(selected_roi[0],selected_roi[1],selected_roi[2],selected_roi[3])
                if system_state.roi_selected is not True:
                    system_state.toggle_roi()
                cv2.destroyWindow("Select ROI")
            elif key == ord('e'):
                if system_state.roi_selected is True:
                    system_state.toggle_roi()
                cv2.destroyAllWindows()
    cv2.destroyAllWindows()