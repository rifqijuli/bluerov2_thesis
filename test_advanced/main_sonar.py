from brping import Ping1D
import logging

log = logging.getLogger("Main Sonar")
log.info("Main Sonar started")

def main_sonar(ping_distance):
    myPing = Ping1D()
    # myPing.connect_serial("/dev/ttyUSB0", 115200)
    # For UDP
    myPing.connect_udp("192.168.2.2", 9090)
    while True:
        try:
            if myPing.initialize() is False:
                print("Failed to initialize Ping!")
                return None
            data = myPing.get_distance()
            log.info(f"Sonar Distance: {data['distance']} mm")
            if data:
                ping_distance.value = data["distance"]/1000.0  # Convert to meters
            else:
                print("Failed to get distance data")
        except Exception as e:
            print(f"An error occurred: {e}")


