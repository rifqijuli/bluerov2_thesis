import main_vision as vision
import main_control as control
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
    def __init__(self, id, flag):
        super(Process, self).__init__()
        self.id = id
        self.flag = flag
               
    def run(self):
        time.sleep(1)
        match self.flag:
            case "image":
                log.info("I'm the process with id: {}".format(self.id))
                vision.image_main()
            case "control":
                log.info("I'm the process with id: {}".format(self.id))
                control.main_control()
            case "dummy":
                log.info("I'm the process with id: {}".format(self.id))
                while True:
                    time.sleep(0.5)
                    log.info(f"Perbedaan jadi sekian : {horizontalHeadingDifference.get_value('pixel')}")
                    log.info(f"Harusnya Sibuk (True) : {program_state.get_busy_state()}")
                    time.sleep(5)
                    program_state.set_state_to_free()
                    program_state.set_yaw_state_to_free()
                    program_state.set_pitch_state_to_free()
                    log.info(f"Harusnya Free (False) : {program_state.get_busy_state()}")
        
if __name__ == '__main__':
    p = Process(0,"image")
    p.start()
    p = Process(1,"control")
    p.start()
    #p = Process(2,"dummy")
    #p.start()