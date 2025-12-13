import main_vision as vision
import main_control as control
import multiprocessing as mp
import time
import logging
from misc import stateLoader as stateLoad

log = logging.getLogger("runner")

logging.basicConfig(level=logging.INFO,
                    format="%(asctime)s [%(name)s] %(levelname)s: %(message)s")
log.info("Runner started")

class program_state():
    state = 'FREE'

    def get_state():
        return program_state.state
    
    def set_state_to_busy():
        program_state.state = 'BUSY'
        return program_state.state
    
    def set_state_to_free():
        program_state.state = 'FREE'
        return program_state.state

#Target object State
class isObjectSelected:
    state = False

    def get_state():
        return isObjectSelected.state
    
    def set_state(state):
        isObjectSelected.state = state
        return isObjectSelected.state

#Difference in Horizontal Heading
class horizontalHeadingDifference:
    value = 0.0

    def get_value():
        return horizontalHeadingDifference.value
    
    def set_value(new_value):
        try:
            float(new_value)
            if program_state.state == 'FREE':
                horizontalHeadingDifference.value = new_value
                log.info(f"New Value [Horizontal Heading] has been set")
            else:
                log.info("Value [Horizontal Heading] has been set already.")
            return horizontalHeadingDifference.value
        except ValueError:
            log.info("Input must be a number.")
            return horizontalHeadingDifference.value
        
#Difference in Vertical Heading
class verticalHeadingDifference:
    value = 0.0

    def get_value():
        return verticalHeadingDifference.value
    
    def set_value(new_value):
        try:
            float(new_value)
            if program_state.state == 'FREE':
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
                    progState = stateLoad.load_state()
                    currentState = stateLoad.getProgramState(progState)
                    log.info(f"MANNTAAPPPUU DJIWAAAAQUUUU : {currentState}")
                    time.sleep(5)
                    stateLoad.setProgramState(False)
                    progState = stateLoad.load_state()
                    currentState = stateLoad.getProgramState(progState)
                    log.info(f"JADIDII GUININN REKK : {currentState}")
                    print(program_state.set_state_to_free())
                    print(horizontalHeadingDifference.get_value())
        
if __name__ == '__main__':
    p = Process(0,"image")
    p.start()
    p = Process(1,"control")
    p.start()
    p = Process(2,"dummy")
    p.start()