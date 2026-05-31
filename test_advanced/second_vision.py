import numpy as np
import cv2
from camera import rov_camera
from ultralytics import YOLO
from tracking import yolo_track, pixel_convert
from collections import defaultdict
import main_state as runner
import logging
from misc import specLoader as spec
from object_detection_model.model_loader import get_model_path

specs = spec.load_specs()

log = logging.getLogger("Second Vision")
log.info("Second Vision started")

#!/usr/bin/env python

#if __name__ == '__main__':
def image_main(
        modelOpt = False, 
        is_program_state_busy = None, 
        is_target_detected = None,
        target_class = None,
        target_id = None,
        is_crane_view = None,
        crane_view_horizontal = None,
        crane_view_vertical = None):
    """
    BlueRov video capture class
    """
    frame_id = 0
    confidence_threshold = 0.2
    iou_threshold = 0.6

    model = YOLO(get_model_path(modelOpt))
    log.info(f"Model {modelOpt['which_model']} on dataset {modelOpt['dataset']} loaded successfully")

    # Target frame size
    class frameSize:
        def __init__(self, width, height):
            self.width = width
            self.height = height
        
        def center(self):
            return (self.width/2, self.height/2)

    log.info('Initialising second video stream...')
    log.info('Press q to quit')
    waited = 0

     # Create the video object
    video = rov_camera.Video(port=spec.get_camera_port(specs))
    while not video.frame_available():
        waited += 1
        print('\r  Frame not available (x{})'.format(waited), end='')
        cv2.waitKey(30)
    log.info('\nSuccess!\nStarting streaming - press "q" to quit.')

    # YOLO Store the track history
    track_history = defaultdict(lambda: []) 

    # Initiate resize frame size
    targetFrame = frameSize(*spec.get_vision_resolution(specs))

    while True:
        if video.frame_available():
            # Only retrieve and display a frame if it's new
            frame = video.frame()
        frame = cv2.resize(frame, (targetFrame.width, targetFrame.height))

        try:
            results = model.track(frame, persist=True,conf=confidence_threshold, iou=iou_threshold, classes=target_class.value)
            if results[0].boxes is not None and len(results[0].boxes) > 0:
                is_crane_view.value = 1 # Set to Crane View
                track_objects = yolo_track.draw_tracker(results[0], track_history, frame, target_id=target_id, frame_id=frame_id) 
                frame = track_objects[0]['frame']

                # Set Heading Difference to runner
                horizontal_diff = track_objects[0]['detected_object']['x_diff']
                vertical_diff = track_objects[0]['detected_object']['y_diff']

                p1 = np.array((0, 0))
                p2 = np.array((horizontal_diff, vertical_diff))

                distance = np.linalg.norm(p2 - p1)
                log.info(f"Distance to target: {distance} pixels")
    
                if abs(horizontal_diff) >= spec.get_tolerance_pixels(specs):
                    crane_view_horizontal.value = horizontal_diff
                else:
                    crane_view_horizontal.value = horizontal_diff
                    log.info("Yaw position accepted")
                
                if abs(vertical_diff) > 0:#ram into center
                    crane_view_vertical.value = vertical_diff
                    runner.verticalHeadingDifference.set_pixel_closeness_value(crane_view_vertical.value)
                else:
                    crane_view_vertical.value = vertical_diff
                    runner.verticalHeadingDifference.set_pixel_closeness_value(crane_view_vertical.value)
                    log.info("Close position accepted")
        except:
            is_crane_view.value = 0
            log.info("Object detection failed, waiting for next frame.")
            log.info(f"Target detected class: {target_class}, Target detected id: {target_id}")
        finally:
            #out.write(frame)
            cv2.namedWindow('CraneView')
            cv2.circle(frame, center=(int(targetFrame.center()[0]), int(targetFrame.center()[1])), radius=5, color=(0, 255, 255), thickness=-1)
            cv2.imshow("CraneView", frame)

            # Allow frame to display, and check if user wants to quit
            key = cv2.waitKey(50)
            if key == ord('q'):
                #runner.program_state.set_state_to_free()
                is_program_state_busy.value = 0 # Set to Free
                is_target_detected.value = 0 # Set to Not Detected
                #out.release()
                break
            elif key == ord('n'):
                # Manual change to near camera setup
                pass
    cv2.destroyAllWindows()