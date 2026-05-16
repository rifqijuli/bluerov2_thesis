from brping import Ping1D
import logging

log = logging.getLogger("Main Sonar")
log.info("Main Sonar started")

def get_sonar_distance(myPing):
    data = myPing.get_distance()
    if data:
        return data["distance"]/1000.0  # Convert to meters
    return None

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
            data = get_sonar_distance(myPing)
            log.info(f"Sonar Distance: {data} mm")
            if data:
                ping_distance.value = data
            else:
                ping_distance.value = ping_distance.value # Keep previous value if failed to get new data
        except Exception as e:
            print(f"An error occurred: {e}")


