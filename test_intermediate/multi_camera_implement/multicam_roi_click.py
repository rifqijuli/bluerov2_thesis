import torch
import torch.nn as nn
import torchvision.transforms as T
import numpy as np
import cv2
import gi
import rov_camera
from ultralytics import YOLO
import string
import yolo_track
from collections import defaultdict

from nets.funiegan import GeneratorFunieGAN as Generator  # adjust import path to match your repo

gi.require_version('Gst', '1.0')
from gi.repository import Gst

# Load the YOLO11 model
model = YOLO("yolo11n.pt")

# FUnIE-GAN
# --- Load pretrained FUnIE-GAN model ---
device = "cuda" if torch.cuda.is_available() else "cpu"
model_path = "funie_generator.pth"  # change if different
G = Generator().to(device)
G.load_state_dict(torch.load(model_path, map_location=device))
G.eval()

# --- Define transforms ---
to_tensor = T.Compose([
    T.ToPILImage(),
    T.Resize((256, 256)),
    T.ToTensor()
])

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

class click_mouse_position:
    x = 0
    y = 0

    def set_position(x_pos, y_pos):
        click_mouse_position.x = x_pos
        click_mouse_position.y = y_pos
    
    def is_within_object(object):
        print(f"Object coords and size: X={object['x_coord']}, Y={object['y_coord']}, Width={object['width']}, Height={object['height']}")
        if (click_mouse_position.x >= object['x_coord'] and click_mouse_position.x <= object['x_coord'] + object['width'] and
            click_mouse_position.y >= object['y_coord'] and click_mouse_position.y <= object['y_coord'] + object['height']):
            return ( object['track_id'])
        else:
            return False


# mouse callback function
def get_click(event,x,y,flags,param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        print(f"Clicked coordinates: X={x}, Y={y}")
        click_mouse_position.set_position(x, y)

#!/usr/bin/env python
"""
BlueRov video capture class
"""

class cameraOpt:
    isROVCamera = False  # Set to True to use ROV camera, False for local webcam    

if __name__ == '__main__':

    print('Initialising stream...')
    print('Press q to quit\nPress s to select ROI')
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
                annotated_frame = results[0].plot()
                track_objects = yolo_track.draw_tracker(results[0], track_history, frame, roi_obj)
                '''
                # handle multiple object detected
                for each in track_objects:
                    annotated_frame_original = each['frame']
                    if each['detected_object'] is not None:
                        detected_object = each['detected_object']
                        print(f"Detected object at X={deteqcted_object['x_coord']}, Y={detected_object['y_coord']}, Width={detected_object['width']}, Height={detected_object['height']}")
                    else:
                        detected_object is None
                '''
            except Exception as e:
                print(f"No object detection in the frame")
                annotated_frame_original = rect_img
            
            #Put it back to frame
            frame[int(roi_obj.y):int(roi_obj.y+roi_obj.height), int(roi_obj.x):int(roi_obj.x+roi_obj.width)] = annotated_frame
            cv2.rectangle(frame, 
                (int(roi_obj.x), int(roi_obj.y)), 
                (int(roi_obj.x + roi_obj.width), int(roi_obj.y + roi_obj.height)),
                (0, 255, 255), 2)
            
            #cv2.imshow('rect_img', annotated_frame)
            #cv2.imshow('resct_img', annotated_frame_original_2)
        except:
            #print("sini")
            pass
        finally:
            # Show both
            cv2.namedWindow('Original')
            cv2.circle(frame, center=(int(targetFrame.center()[0]), int(targetFrame.center()[1])), radius=5, color=(0, 255, 255), thickness=-1)
            cv2.imshow("Original", frame)

            
            if system_state.roi_selected:
                cv2.setMouseCallback('Original', get_click)
                for each in track_objects:
                    isInObject = click_mouse_position.is_within_object(each['detected_object'])
                    print(f"Is within object: {isInObject}")

            # Allow frame to display, and check if user wants to quit
            key = cv2.waitKey(100)
            if key == ord('q'):
                break
            elif key == ord('s'):
                showCrosshair = False
                fromCenter = False
                selected_roi = cv2.selectROI("Select ROI", frame, fromCenter, showCrosshair)
                roi_obj = roi_image(selected_roi[0],selected_roi[1],selected_roi[2],selected_roi[3])
                system_state.toggle_roi()
                cv2.destroyWindow("Select ROI")
    cv2.destroyAllWindows()