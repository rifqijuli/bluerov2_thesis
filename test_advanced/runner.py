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

class program_state():

    def get_busy_state():
        progState = stateLoad.load_state()
        currentState = stateLoad.getProgramState(progState)
        return currentState
    
    def set_state_to_busy():
        stateLoad.setProgramState(True)
        return program_state.get_busy_state()
    
    def set_state_to_free():
        stateLoad.setProgramState(False)
        return program_state.get_busy_state()

#Target object State
class isObjectSelected:
    state = False

    def get_busy_state():
        return isObjectSelected.state
    
    def set_state(state):
        isObjectSelected.state = state
        return isObjectSelected.state

#Difference in Horizontal Heading
class horizontalHeadingDifference:

    def get_value(flag):
        load_difference = heading_difference_loader.load_difference()
        current_yaw_difference = heading_difference_loader.get_yaw_difference(load_difference)
        pixel_difference, degree_difference = current_yaw_difference
        match flag:
            case "pixel":
                return pixel_difference
            case "degree":
                return degree_difference
            case "all":
                return {
                    pixel_difference : pixel_difference,
                    degree_difference : degree_difference
                }
    
    def set_value(new_value):
        try:
            float(new_value)
            if program_state.get_busy_state() == False:
                heading_difference_loader.set_yaw_difference(pixel_difference=new_value)
                log.info(f"New Value [Horizontal Heading] has been set")
            else:
                log.info("Value [Horizontal Heading] has been set already.")
            return horizontalHeadingDifference.get_value("pixel")
        except ValueError:
            log.info("Input must be a number.")
            return horizontalHeadingDifference.get_value("pixel")
        
#Difference in Vertical Heading
class verticalHeadingDifference:
    value = 0.0

    def get_value():
        return verticalHeadingDifference.value
    
    def set_value(new_value):
        try:
            float(new_value)
            if program_state.get_busy_state() == False:
                verticalHeadingDifference.value = new_value
                log.info(f"New Value [Vertical Heading] has been set")
            else:
                log.info("Value [Vertical Heading] has been set already.")
            return verticalHeadingDifference.value
        except ValueError:
            log.info("Input must be a number.")
            return verticalHeadingDifference.value

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
                #control.main_control()
            case "dummy":
                log.info("I'm the process with id: {}".format(self.id))
                while True:
                    time.sleep(1)
                    log.info(f"MANNTAAPPPUU DJIWAAAAQUUUU : {program_state.get_busy_state()}")
                    time.sleep(5)
                    program_state.set_state_to_free()
                    stateLoad.setProgramState(False)
                    log.info(f"JADIDII GUININN REKK : {program_state.get_busy_state()}")
                    log.info(f"Perbedaan jadi sekian : {horizontalHeadingDifference.get_value('pixel')}")
        
if __name__ == '__main__':
    p = Process(0,"image")
    p.start()
    p = Process(1,"control")
    p.start()
    p = Process(2,"dummy")
    p.start()