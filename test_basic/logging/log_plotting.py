# plot_from_csv.py
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np

df = pd.read_csv("detections.csv")
if df.empty:
    print("No detections logged.")
    exit()

# per-frame aggregations
df["area"] = df["w"] * df["h"]

# Plot confidence over time (by frame index)
plt.figure(figsize=(10,4))
plt.scatter(df["frame_idx"], df["conf"], s=6, alpha=0.6)
plt.xlabel("frame index")
plt.ylabel("confidence")
plt.title("Detection confidence per detection")
plt.grid(True)
plt.savefig("conf_vs_frame.png", dpi=150)

# Plot bbox area over time
plt.figure(figsize=(10,4))
plt.scatter(df["frame_idx"], df["area"], s=6, alpha=0.6)
plt.xlabel("frame index")
plt.ylabel("bbox area (pixels)")
plt.title("BBox area per detection")
plt.grid(True)
plt.savefig("area_vs_frame.png", dpi=150)

# Detections per frame
counts = df.groupby("frame_idx").size()
plt.figure(figsize=(10,3))
plt.plot(counts.index, counts.values)
plt.xlabel("frame index")
plt.ylabel("num detections")
plt.title("Detections per frame")
plt.grid(True)
plt.savefig("dets_per_frame.png", dpi=150)

print("Plots saved: conf_vs_frame.png, area_vs_frame.png, dets_per_frame.png")
plt.show()