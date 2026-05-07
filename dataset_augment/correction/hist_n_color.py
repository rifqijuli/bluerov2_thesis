import numpy as np
import cv2
import os

from PIL import Image
from skimage.exposure import match_histograms

alpha = 0.05

def histogram_matching(source, target):
    # Match histograms for each channel
    matched_lab = match_histograms(source, target, channel_axis=-1).astype(np.float32)

    return matched_lab

def read_file(sn,tn):
    s = cv2.imread('source/'+sn+'.jpg').astype(np.float32) / 255.0
    s = cv2.cvtColor(s,cv2.COLOR_BGR2LAB)
    t = cv2.imread('target/'+tn+'.jpg').astype(np.float32) / 255.0
    t = cv2.cvtColor(t,cv2.COLOR_BGR2LAB)
    return s, t

def get_mean_and_std(x):
    x_mean, x_std = cv2.meanStdDev(x)
    x_mean = np.hstack(np.around(x_mean,2))
    x_std = np.hstack(np.around(x_std,2))
    return x_mean, x_std

def color_transfer_function(s, t):
    height, width, channel = s.shape
    s_mean, s_std = get_mean_and_std(s)
    t_mean, t_std = get_mean_and_std(t)
    
    for i in range(0,height):
        for j in range(0,width):
            for k in range(0,channel):
                x = s[i,j,k]
                x = ((x-s_mean[k])*(t_std[k]/(s_std[k])))+t_mean[k]
                # round or +0.5
                # x = round(x)
                x = round(x + alpha * (x - s[i,j,k]))
                # boundary check
                x = 0 if x<0 else x
                x = 255 if x>255 else x
                s[i,j,k] = x
    
    return s[i,j,k]

def color_transfer(image = None):
    # sources = ['s1','s2','s3','s4','s5','s6']
    if image is not None:
        sources = [image]
        targets = ['sea','lake','pool']
    else:
        sources = sorted([os.path.splitext(f)[0] for f in os.listdir('source') if f.endswith('.jpg')])
        targets = ['t1']

    for n in range(len(sources)):
        print("Converting picture"+str(n+1)+"...")
        if image is not None:
            s = np.array(sources[0])
            s = s[..., ::-1].astype(np.float32) / 255.0 # Convert RGB to BGR
            s = cv2.cvtColor(s,cv2.COLOR_BGR2LAB)
            s_lake = s
            s_sea = s

            t = cv2.imread('target/'+targets[2]+'.png').astype(np.float32) / 255.0
            t = cv2.cvtColor(t,cv2.COLOR_BGR2LAB)
            t_lake = cv2.imread('target/'+targets[1]+'.png').astype(np.float32) / 255.0
            t_lake = cv2.cvtColor(t_lake,cv2.COLOR_BGR2LAB)
            t_sea = cv2.imread('target/'+targets[0]+'.png').astype(np.float32) / 255.0
            t_sea = cv2.cvtColor(t_sea,cv2.COLOR_BGR2LAB)

            matched = histogram_matching(s, t)
            matched_lake = histogram_matching(s, t_lake)
            matched_sea = histogram_matching(s, t_sea)

            hist_out = cv2.cvtColor(matched, cv2.COLOR_LAB2BGR)
            hist_out_lake = cv2.cvtColor(matched_lake, cv2.COLOR_LAB2BGR)
            hist_out_sea = cv2.cvtColor(matched_sea, cv2.COLOR_LAB2BGR)

            matched = color_transfer_function(matched,t)
            matched_lake = color_transfer_function(matched_lake, t_lake)
            matched_sea = color_transfer_function(matched_sea, t_sea)

            s = color_transfer_function(s,t)
            s_lake = color_transfer_function(s_lake,t_lake)
            s_sea = color_transfer_function(s_sea, t_sea)

        else:
            s, t = read_file(sources[n],targets[0])
            matched = histogram_matching(s, t)
            hist_out = cv2.cvtColor(matched, cv2.COLOR_LAB2BGR)
            t_mean, t_std = get_mean_and_std(t)
            m_mean, m_std = get_mean_and_std(matched)
            height, width, channel = matched.shape
            for i in range(0,height):
                for j in range(0,width):
                    for k in range(0,channel):
                        x = matched[i,j,k]
                        x = ((x-m_mean[k])*(t_std[k]/(m_std[k])))+t_mean[k]
                        # round or +0.5
                        x = round(x)
                        # boundary check
                        x = 0 if x<0 else x
                        x = 255 if x>255 else x
                        matched[i,j,k] = x

        #matched = np.clip(matched, 0, 1)
        out = cv2.cvtColor(matched,cv2.COLOR_LAB2BGR)
        cv2.imwrite('hist_result/r'+str(n+1)+'.jpg', np.clip(hist_out * 255, 0, 255).astype(np.uint8))
        cv2.imwrite('result/r'+str(n+1)+'.jpg', np.clip(out * 255, 0, 255).astype(np.uint8))
        hist_out = hist_out[..., ::-1]  # Convert back to RGB
        hist_out = Image.fromarray(np.clip(hist_out * 255, 0, 255).astype(np.uint8))

    if image is not None:
        out_lake = cv2.cvtColor(matched_lake,cv2.COLOR_LAB2BGR)
        out_sea = cv2.cvtColor(matched_sea,cv2.COLOR_LAB2BGR)

        out_reinhardt = cv2.cvtColor(s,cv2.COLOR_LAB2BGR)
        out_lake_reinhardt = cv2.cvtColor(s_lake,cv2.COLOR_LAB2BGR)
        out_sea_reinhardt = cv2.cvtColor(s_sea,cv2.COLOR_LAB2BGR)

        hist_out_lake = hist_out_lake[..., ::-1]  # Convert back to RGB
        hist_out_sea = hist_out_sea[..., ::-1]  # Convert back to RGB
        hist_out_lake = Image.fromarray(np.clip(hist_out_lake * 255, 0, 255).astype(np.uint8))
        hist_out_sea = Image.fromarray(np.clip(hist_out_sea * 255, 0, 255).astype(np.uint8))

        out = out[..., ::-1]  # Convert back to RGB
        out_lake = out_lake[..., ::-1]  # Convert back to RGB
        out_sea = out_sea[..., ::-1]  # Convert back to RGB

        out_reinhardt = out_reinhardt[..., ::-1]  # Convert back to RGB
        out_lake_reinhardt = out_lake_reinhardt[..., ::-1]  # Convert back to RGB
        out_sea_reinhardt = out_sea_reinhardt[..., ::-1]  # Convert back to RGB
        
        out = Image.fromarray(np.clip(out * 255, 0, 255).astype(np.uint8))
        out_lake = Image.fromarray(np.clip(out_lake * 255, 0, 255).astype(np.uint8))
        out_sea = Image.fromarray(np.clip(out_sea * 255, 0, 255).astype(np.uint8))

        out_reinhardt = Image.fromarray(np.clip(out_reinhardt * 255, 0, 255).astype(np.uint8))
        out_lake_reinhardt = Image.fromarray(np.clip(out_lake_reinhardt * 255, 0, 255).astype(np.uint8))
        out_sea_reinhardt = Image.fromarray(np.clip(out_sea_reinhardt * 255, 0, 255).astype(np.uint8))
        return out, hist_out, out_lake, hist_out_lake, out_sea, hist_out_sea, out_reinhardt, out_lake_reinhardt, out_sea_reinhardt
    
color_transfer()
os.system("pause")