import csv
import time
from pathlib import Path


class PIDLogger:
    def __init__(self, filepath="pid_log.csv"):
        self.filepath = Path(filepath)
        self._file = open(self.filepath, "w", newline="")
        self._writer = csv.writer(self._file)
        self._writer.writerow([
            "timestamp", "processing_time",
            "pixel_error_x", "pixel_error_y", "sonar_distance",
            "yaw_pid_output", "pitch_pid_output", "forward_pid_output",
            "pwm_yaw", "pwm_pitch", "pwm_forward",
        ])
        self._file.flush()

    def log(self, 
            timestamp, processing_time,
            pixel_error_x, pixel_error_y, sonar_distance,
            yaw_out, pitch_out, forward_out,
            pwm_yaw, pwm_pitch, pwm_forward
            ):
        self._writer.writerow([
            timestamp, processing_time,
            pixel_error_x, pixel_error_y, sonar_distance,
            yaw_out, pitch_out, forward_out,
            pwm_yaw, pwm_pitch, pwm_forward
        ])
        self._file.flush()

    def close(self):
        self._file.close()