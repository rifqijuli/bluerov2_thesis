FROM osrf/ros:noetic-desktop-full
LABEL authors="rifqijuli"
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y python3-pip && rm -rf /var/lib/apt/lists/*

RUN pip3 install --upgrade pip
# no extra Python packages needed for this simple subscriber

WORKDIR /root/ros_consumer
COPY src/ ./src/
RUN chmod +x src/imu_subscriber.py

CMD bash -lc "sleep 2 && python3 /root/consumer/src/imu_subscriber.py"