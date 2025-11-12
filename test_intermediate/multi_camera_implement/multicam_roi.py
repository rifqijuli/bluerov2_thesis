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
        frame = cv2.resize(frame, (640, 480))
        
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
                results = model.track(out_bgr, persist=True,conf=0.6, iou=0.3, classes=[0])[0]
                annotated_frame_original = yolo_track.draw_tracker(results, track_history)
            except Exception as e:
                print(f"No object detection in the frame")
                annotated_frame_original = out_bgr
            
            #Put it back to frame
            frame[int(roi_obj.y):int(roi_obj.y+roi_obj.height), int(roi_obj.x):int(roi_obj.x+roi_obj.width)] = annotated_frame_original
            cv2.rectangle(frame, 
                (int(roi_obj.x), int(roi_obj.y)), 
                (int(roi_obj.x + roi_obj.width), int(roi_obj.y + roi_obj.height)),
                (0, 255, 255), 2)
            
            #cv2.imshow('rect_img', annotated_frame_original)
        except:
            #print("sini")
            pass
        finally:
            # Show both
            cv2.imshow("Original", frame)

            # Allow frame to display, and check if user wants to quit
            key = cv2.waitKey(50)
            if key == ord('q'):
                break
            elif key == ord('s'):
                showCrosshair = False
                fromCenter = False
                selected_roi = cv2.selectROI("Select ROI", frame, fromCenter, showCrosshair)
                roi_obj = roi_image(selected_roi[0],selected_roi[1],selected_roi[2],selected_roi[3])
                cv2.destroyWindow("Select ROI")
    cv2.destroyAllWindows()