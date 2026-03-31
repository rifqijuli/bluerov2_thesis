from brping import Ping1D
myPing = Ping1D()

myPing.connect_udp("192.168.2.2", 9090)

def get_distance(master):
    myPing = brping.Ping1D()
    # myPing.connect_serial("/dev/ttyUSB0", 115200)
    # For UDP
    myPing.connect_udp("192.168.2.2", 9090)
    try:
        if myPing.initialize() is False:
            print("Failed to initialize Ping!")
            return None
        data = myPing.get_distance()
        if data:
            return data["distance"]
        else:
            print("Failed to get distance data")
            return None
    except Exception as e:
        print(f"An error occurred: {e}")
        return None
    finally:        
        myPing.close()
    

