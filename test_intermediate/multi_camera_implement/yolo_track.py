from ultralytics import YOLO
import numpy as np
import cv2

class coord_difference:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

class coordinate:
    def __init__(self, x_coord, y_coord, frame):
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.frame = frame
    
    def difference_to_frame(self):
        (h, w) = self.frame.shape[:2]
        frame_center_x = w / 2
        frame_center_y = h / 2
        x_diff = self.x_coord - frame_center_x
        y_diff = self.y_coord - frame_center_y
        return coord_difference(x_diff, y_diff, 0)
    
def draw_tracker(model_result, track_history, main_frame=None, roi_object=None):
    # Get the boxes and track IDs
    if model_result.boxes and model_result.boxes.is_track:
        boxes = model_result.boxes.xywh.cpu()
        track_ids = model_result.boxes.id.int().cpu().tolist()

        # Visualize the result on the frame
        frame = model_result[0].plot()
        
        # Plot the tracks
        for box, track_id in zip(boxes, track_ids):
            x, y, w, h = box
            if main_frame is not None:
                tracker_to_center(x, y, w, h, main_frame, roi_object)
            else:
                tracker_to_center(x, y, w, h, frame)
            track = track_history[track_id]
            track.append((float(x), float(y)))  # x, y center point
            if len(track) > 30:  # retain 30 tracks for 30 frames
                track.pop(0)

            # Draw the tracking lines
            points = np.hstack(track).astype(np.int32).reshape((-1, 1, 2))
            cv2.polylines(frame, [points], isClosed=False, color=(230, 230, 230), thickness=10)
    return frame

def reset_tracker(track_history):
    track_history.clear()


def tracker_to_center(x_coord, y_coord, width, height, frame, roi_object=None):
    # Calculate center of the bounding box
    diff_to_center = coordinate((x_coord + roi_object.x) , (y_coord + roi_object.y), frame).difference_to_frame()
    print(f"Coordinate difference to center - X: {diff_to_center.x}, Y: {diff_to_center.y}, Z: {diff_to_center.z}")
    return True
