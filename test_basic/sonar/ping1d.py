from brping import Ping1D
myPing = Ping1D()
# myPing.connect_serial("/dev/ttyUSB0", 115200)
# For UDP
myPing.connect_udp("192.168.2.2", 9090)

if myPing.initialize() is False:
    print("Failed to initialize Ping!")
    exit(1)

while True:
    data = myPing.get_distance()
    distance = data["distance"]/1000  # Convert from mm to m
    if data:
        print("Distance: %sm\tConfidence: %s%%" % (distance, data["confidence"]))
    else:
        print("Failed to get distance data")