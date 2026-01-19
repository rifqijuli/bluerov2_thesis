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
    
    def get_yaw_busy_state():
        progState = stateLoad.load_state()
        currentState = stateLoad.get_yaw_state(progState)
        return currentState
    
    def get_pitch_busy_state():
        progState = stateLoad.load_state()
        currentState = stateLoad.get_pitch_state(progState)
        return currentState
    
    def set_yaw_state_to_busy():
        stateLoad.set_yaw_state(True)
        return program_state.get_yaw_busy_state()
    
    def set_yaw_state_to_free():
        stateLoad.set_yaw_state(False)
        return program_state.get_yaw_busy_state()
    
    def set_pitch_state_to_busy():
        stateLoad.set_pitch_state(True)
        return program_state.get_pitch_busy_state()
    
    def set_pitch_state_to_free():
        stateLoad.set_pitch_state(False)
        return program_state.get_pitch_busy_state()

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
    
    def set_pixel_value(new_value):
        try:
            # Approach 1
            '''
            float(new_value)
            if program_state.get_yaw_busy_state() == False:
                heading_difference_loader.set_yaw_difference(pixel_difference=new_value)
                log.info(f"New Value [Horizontal Heading] has been set")
            else:
                log.info("Value [Horizontal Heading] has been set already.")
            '''
            # Approach 2
            heading_difference_loader.set_yaw_difference(pixel_difference=new_value)
            log.info(f"New Value [Horizontal Heading] has been set")

            return horizontalHeadingDifference.get_value("pixel")
        except ValueError:
            log.info("Input must be a number.")
            return horizontalHeadingDifference.get_value("pixel")
        
    def set_degree_value(new_value):
        try:
            float(new_value)
            # Approach 1
            '''
            if program_state.get_yaw_busy_state() == False:
                heading_difference_loader.set_yaw_difference(degree_difference=new_value)
                log.info(f"New Value [Horizontal Heading] has been set")
            else:
                log.info("Value [Horizontal Heading] has been set already.")
            '''
            # Approach 2
            heading_difference_loader.set_yaw_difference(degree_difference=new_value)
            log.info(f"New Value [Horizontal Heading] has been set")

            return horizontalHeadingDifference.get_value("degree")
        except ValueError:
            log.info("Input must be a number.")
            return horizontalHeadingDifference.get_value("degree")
        
        
#Difference in Vertical Heading
class verticalHeadingDifference:

    def get_value(flag):
        load_difference = heading_difference_loader.load_difference()
        current_pitch_difference = heading_difference_loader.get_pitch_difference(load_difference)
        pixel_difference, degree_difference = current_pitch_difference
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
    
    def set_pixel_value(new_value):
        try:
            float(new_value)

            # Approach 1
            '''
            if program_state.get_pitch_busy_state() == False:
                heading_difference_loader.set_pitch_difference(pixel_difference=new_value)
                log.info(f"New Value [Vertical Heading] has been set")
            else:
                log.info("Value [Vertical Heading] has been set already.")
            '''
            
            # Approach 2
            heading_difference_loader.set_pitch_difference(pixel_difference=new_value)
            log.info(f"New Value [Vertical Heading] has been set")

            return verticalHeadingDifference.get_value("pixel")
        except ValueError:
            log.info("Input must be a number.")
            return verticalHeadingDifference.get_value("pixel")

    def set_degree_value(new_value):
        try:
            float(new_value)

            # Approach 1
            '''
            if program_state.get_pitch_busy_state() == False:
                heading_difference_loader.set_pitch_difference(degree_difference=new_value)
                log.info(f"New Value [Vertical Heading] has been set")
            else:
                log.info("Value [Vertical Heading] has been set already.")
            '''
            # Approach 2
            heading_difference_loader.set_pitch_difference(degree_difference=new_value)
            log.info(f"New Value [Vertical Heading] has been set")

            return verticalHeadingDifference.get_value("degree")
        except ValueError:
            log.info("Input must be a number.")
            return verticalHeadingDifference.get_value("degree")

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