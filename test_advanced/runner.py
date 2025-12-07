import main_vision as vision
import multiprocessing as mp
import time

class program_state():
    state = 'FREE'

    def get_state():
        return program_state.state
    
    def set_state_to_busy(state):
        program_state.state = 'BUSY'
        return program_state.state
    
    def set_state_to_free(state):
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
class differenceInHorizontalHeading:
    value = 0.0

    def get_value():
        return differenceInHorizontalHeading.value
    
    def set_value(new_value):
        try:
            float(new_value)
            if program_state.state == 'FREE':
                differenceInHorizontalHeading.value = new_value
                program_state.state = 'BUSY'
                print(f"New Value has been set")
            else:
                print("Value has been set already.")
            return differenceInHorizontalHeading.value
        except ValueError:
            print("Input must be a number.")
            return differenceInHorizontalHeading.value

class Process(mp.Process):
    def __init__(self, id, flag):
        super(Process, self).__init__()
        self.id = id
        self.flag = flag
               
    def run(self):
        time.sleep(1)
        match self.flag:
            case "image":
                print("I'm the process with id: {}".format(self.id))
                vision.image_main()
            case "control":
                print("I'm the process with id: {}".format(self.id))
        
if __name__ == '__main__':
    p = Process(0,"image")
    p.start()
    p = Process(1,"control")
    p.start()