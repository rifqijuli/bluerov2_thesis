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

#!/usr/bin/env python
"""
BlueRov video capture class
"""

class cameraOpt:
    isROVCamera = False  # Set to True to use ROV camera, False for local webcam    

if __name__ == '__main__':
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
    to_image = T.ToPILImage()

    print('Initialising stream...')
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
        
        # Convert frame (BGR->RGB)
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        inp = to_tensor(rgb).unsqueeze(0).to(device)

        # Run enhancement
        with torch.no_grad():
            out = G(inp)

        # Convert back to OpenCV format
        out_np = out.squeeze(0).cpu().permute(1, 2, 0).numpy()
        out_np = np.clip(out_np * 255, 0, 255).astype(np.uint8)
        out_bgr = cv2.cvtColor(out_np, cv2.COLOR_RGB2BGR)

        # Resize for display
        out_bgr = cv2.resize(out_bgr, (frame.shape[1], frame.shape[0]))

        #FIRST I WILL TRACK AND DETECT ALL OF THEM, WHEN I CLICK, 
        #I CHOOSE THE ARRAY INDEX OF THE PERSON I WANT TO TRACK
        #THEN I WILL ONLY TRACK THAT PERSON USING THE TRACK ID
        #Know it because of the [0] in reults original only tracks the person.

        # Run YOLO11 tracking on the frame, persisting tracks between frames
        # Only track person
        #results_original = model.track(frame, persist=True)[0]

        # Track All
        results_original = model.track(frame, persist=True)
        #results_enhanced = model.track(out_bgr, persist=True)

        #FIRST I WILL TRACK AND DETECT ALL OF THEM, WHEN I CLICK, 
        #I CHOOSE THE ARRAY INDEX OF THE PERSON I WANT TO TRACK
        #THEN I WILL ONLY TRACK THAT PERSON USING THE TRACK ID

        # Visualize the results on the frame
        # Tracker for original using yolo_track module and center difference
        #annotated_frame_original = yolo_track.draw_tracker(results_original, track_history)

        # Tracker for original using yolo_track module with no center difference
        annotated_frame_original = results_original[0].plot()
        #annotated_frame_enhanced = results_enhanced[0].plot()

        # Show both
        #cv2.imshow("Original", frame)
        #cv2.imshow("Enhanced", out_bgr)
        cv2.imshow("YOLO11 Tracking Original", annotated_frame_original)
        #cv2.imshow("YOLO11 Tracking Enhanced", annotated_frame_enhanced)
        # Allow frame to display, and check if user wants to quit
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    cv2.destroyAllWindows()