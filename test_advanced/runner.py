import main_vision as vision
import main_control as control
import main_state as state
import main_cleaner as cleaner
import main_rc_command as rc_command
import main_sonar as sonar
import multiprocessing as mp
import time
import logging
from misc import stateLoader as stateLoad
from misc import heading_difference_loader as heading_difference_loader

log = logging.getLogger("runner")

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
log.info("Runner started")

class Process(mp.Process):
    def __init__(self, id, flag, camera_opt=None, model_opt=None, rc_pwm=None, is_program_state_busy=None, ping_distance=None):
        super(Process, self).__init__()
        self.id = id
        self.flag = flag
        self.camera_opt = camera_opt
        self.model_opt = model_opt or {}
        self.rc_pwm = rc_pwm
        self.is_program_state_busy = is_program_state_busy
        self.ping_distance = ping_distance
        
               
    def run(self):
        time.sleep(1)
        match self.flag:
            case "image":
                log.info("I'm the process with id: {}".format(self.id))
                vision.image_main(
                    cameraOpt=self.camera_opt, 
                    modelOpt=self.model_opt,
                    rc_pwm=self.rc_pwm, 
                    is_program_state_busy=self.is_program_state_busy,
                    ping_distance=self.ping_distance)
            case "control":
                log.info("I'm the process with id: {}".format(self.id))
                control.main_control(
                    rc_pwm=self.rc_pwm, 
                    is_program_state_busy=self.is_program_state_busy,
                    ping_distance=self.ping_distance)
            case "cleaner":
                log.info("I'm the process with id: {}".format(self.id))
                cleaner.main_cleaner()
            case "rc_command":
                log.info("I'm the process with id: {}".format(self.id))
                rc_command.main_rc_command(rc_pwm=self.rc_pwm, 
                                           is_program_state_busy=self.is_program_state_busy,
                                           ping_distance=self.ping_distance)
            case "ping_sonar":
                log.info("I'm the process with id: {}".format(self.id))
                sonar.main_sonar(ping_distance=self.ping_distance)
            case "dummy":
                log.info("I'm the process with id: {}".format(self.id))
                while True:
                    time.sleep(0.5)
                    log.info(f"Perbedaan jadi sekian : {state.horizontalHeadingDifference.get_value('pixel')}")
                    log.info(f"Harusnya Sibuk (True) : {state.program_state.get_busy_state()}")
                    time.sleep(5)
                    state.program_state.set_state_to_free()
                    state.program_state.set_yaw_state_to_free()
                    state.program_state.set_pitch_state_to_free()
                    log.info(f"Harusnya Free (False) : {state.program_state.get_busy_state()}")

'''
if __name__ == '__main__':
    p1 = Process(0,"image", 
                 camera_opt="bluerov", 
                 model_opt={
                     "use_cou": True, 
                     "which_model": "yolo26s"
                     })
    p1.start()
    p2 = Process(1,"control")
    p2.start()

    try:
        p1.join()
        p2.join()
    except KeyboardInterrupt:
        p1.terminate()
        p2.terminate()
        p1.join(timeout=1)
        p2.join(timeout=1)

        p3 = Process(2,"cleaner")
        p3.start()


    #p = Process(2,"dummy")
    #p.start()   
'''    


