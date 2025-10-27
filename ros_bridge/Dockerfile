FROM osrf/ros:noetic-desktop-full
LABEL authors="rifqijuli"
# noninteractive
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y \
    python3-pip python3-catkin-pkg-modules python3-rospkg-modules \
    && rm -rf /var/lib/apt/lists/*

# install pymavlink
RUN pip3 install --upgrade pip
RUN pip3 install pymavlink

# Copy code
WORKDIR /root/ros_bridge
COPY src/ ./src/

# Make script executable
RUN chmod +x src/imu_bridge.py

# Launch script (roscore + bridge)
CMD bash -lc "roscore & sleep 2 && python3 /root/imu_bridge/src/imu_bridge.py"