import numpy as np
import cv2
 
cap = cv2.VideoCapture(0)

class roi_image:
    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

if not cap.isOpened():
    print("Cannot open camera")
    exit()

print("Press Q to quit, press S to select ROI")
while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    try:
        rect_img = frame[int(roi_obj.y):int(roi_obj.y+roi_obj.height), int(roi_obj.x):int(roi_obj.x+roi_obj.width)]
        # Do process to the selected image here
        gray = cv2.cvtColor(rect_img, cv2.COLOR_BGR2GRAY)
        
        #Put it back to frame
        gray_bgr = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        frame[int(roi_obj.y):int(roi_obj.y+roi_obj.height), int(roi_obj.x):int(roi_obj.x+roi_obj.width)] = gray_bgr
        cv2.rectangle(frame, 
            (int(roi_obj.x), int(roi_obj.y)), 
            (int(roi_obj.x + roi_obj.width), int(roi_obj.y + roi_obj.height)),
            (0, 255, 255), 2)
        #cv2.imshow('rect_img', gray)
    except:
        print("sini")
        pass
    finally:
         # if frame is read correctly ret is True
        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break
        # Display the resulting frame
        cv2.imshow('frame', frame)
        clicked = cv2.waitKey(1)
        if clicked == ord('q'):
            break
        elif clicked == ord('s'):
            showCrosshair = False
            fromCenter = False
            selected_roi = cv2.selectROI("Image", frame, fromCenter, showCrosshair)
            roi_obj = roi_image(selected_roi[0],selected_roi[1],selected_roi[2],selected_roi[3])
   
# When everything done, release the capture
cap.release()
cv2.destroyAllWindows()