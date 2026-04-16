import tkinter as tk
from tkinter import ttk
import multiprocessing as mp
from runner import Process  # replace with your filename

mp.set_start_method("spawn", force=True)

class RunnerGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("BLUEROV Runner")
        self.geometry("300x320")

        # Process references
        self.procs = {}


        self.allowed_models = {
            "COCO": ["yolo11n", "yolo11s", "yolo26n", "yolo26s"],
            "COU": ["yolo11n", "yolo11s", "yolo26n", "yolo26s"],
            "TrashCan": ["yolo11n", "yolo11s", "yolo26n", "yolo26s"],
            "Pepsi_DTU": ["yolo26n", "yolo26s"],
            "Pepsi_DTU_Rotate": ["yolo26n", "yolo26s"],
            "Pepsi": ["yolo26n"],
            "UNO": ["yolo26n", "yolo26s"],
            "Venise": ["yolo26s", "yolo26n"],
            "Morgane": ["yolo26n", "yolo26s"],
            "Walia": ["yolo26n"]
        }

        # Options
        tk.Label(self, text="Camera:").pack(pady=2)
        self.camera_var = tk.StringVar(value="bluerov")
        self.camera_cb = ttk.Combobox(
            self,
            textvariable=self.camera_var,
            values=["bluerov", "webcam"],
            state="readonly"
        )
        self.camera_cb.pack()

        tk.Label(self, text="Model:").pack(pady=2)
        self.model_var = tk.StringVar(value="yolo26s")
        self.model_cb = ttk.Combobox(
            self,
            textvariable=self.model_var,
            values=["yolo11n", "yolo11s", "yolo26n", "yolo26s"],
            state="readonly"
        )
        self.model_cb.pack()

        tk.Label(self, text="Dataset:").pack(pady=2)
        self.dataset_var = tk.StringVar(value="Pepsi_DTU")
        self.dataset_cb = ttk.Combobox(
            self,
            textvariable=self.dataset_var,
            values=["COCO", "COU", "TrashCan", "Pepsi_DTU", "Pepsi_DTU_Rotate", "UNO", "Venise", "Morgane", "Walia"],
            state="readonly"
        )
        self.dataset_cb.pack()

        self.dataset_cb.bind("<<ComboboxSelected>>", self.on_dataset_change)
        self.on_dataset_change()  # apply initial rule

        # Buttons
        tk.Button(self, text="Start Image+Control", command=self.start_main).pack(pady=5)
        tk.Button(self, text="Stop Main", command=self.stop_main).pack(pady=2)
        tk.Button(self, text="Run Cleaner", command=self.run_cleaner).pack(pady=2)

        # Status
        self.status_var = tk.StringVar(value="Ready")
        tk.Label(self, textvariable=self.status_var).pack(pady=10)

    def on_dataset_change(self, event=None):
        dataset = self.dataset_var.get()
        valid_models = self.allowed_models.get(dataset, ["yolo11n", "yolo11s", "yolo26n", "yolo26s"])

        self.model_cb["values"] = valid_models

        if self.model_var.get() not in valid_models:
            self.model_var.set(valid_models[0])

    def start_main(self):
        if 0 not in self.procs or not self.procs[0].is_alive():

            manager = mp.Manager()
            rc_pwm = manager.list([65535] * 18)
            is_program_state_busy = manager.Value('i', 0)  # 0: free, 1: busy
            ping_distance = manager.Value('d', 0.0)  # Shared ping distance
            is_target_close = manager.Value('i', 0) # 0: far, 1: close

            self.procs[0] = Process(0, "image",
                                  camera_opt=self.camera_var.get(),
                                  model_opt={"dataset": self.dataset_var.get(), "which_model": self.model_var.get()},
                                  rc_pwm=rc_pwm, 
                                  is_program_state_busy=is_program_state_busy, 
                                  ping_distance=ping_distance, 
                                  is_target_close=is_target_close)
            self.procs[0].start()
            self.procs[1] = Process(1, "control", 
                                    rc_pwm=rc_pwm, 
                                    is_program_state_busy=is_program_state_busy, 
                                    ping_distance=ping_distance, 
                                    is_target_close=is_target_close)
            self.procs[1].start()
            self.procs[3] = Process(3, "rc_command", 
                                    rc_pwm=rc_pwm, 
                                    is_program_state_busy=is_program_state_busy, 
                                    ping_distance=ping_distance, 
                                    is_target_close=is_target_close)
            self.procs[3].start()
            self.procs[4] = Process(4, "ping_sonar", 
                                    rc_pwm=rc_pwm, 
                                    is_program_state_busy=is_program_state_busy,
                                    ping_distance=ping_distance, 
                                    is_target_close=is_target_close)
            self.procs[4].start()
            self.status_var.set("Main processes started")

    def stop_main(self):
        for pid in [0, 1, 3, 4]:  # Image, Control, RC Command, Ping Sonar
            if pid in self.procs and self.procs[pid].is_alive():
                self.procs[pid].terminate()
                self.procs[pid].join(timeout=1)
        self.status_var.set("Main stopped")

    def run_cleaner(self):
        p = Process(2, "cleaner")
        p.start()
        self.status_var.set("Cleaner started")

if __name__ == "__main__":
    app = RunnerGUI()
    app.mainloop()
