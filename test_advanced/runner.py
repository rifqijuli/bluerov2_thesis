import multicam_roi_click as mrc
import multiprocessing as mp
import time

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
                mrc.image_main()
            case "control":
                print("I'm the process with id: {}".format(self.id))
        

if __name__ == '__main__':
    p = Process(0,"image")
    p.start()
    p = Process(1,"control")
    p.start()