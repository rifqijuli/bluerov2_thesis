#!/usr/bin/env python3
"""
imu_bridge.py

Connects to MAVLink UDP (BlueOS default) and publishes a ROS sensor_msgs/Imu on /rov/imu.
It uses pymavlink HIGHRES_IMU if available; falls back to ATTITUDE.
Adjust the MAVLINK_URL variable to your BlueOS IP/port if needed.
"""

import time
import rospy
from sensor_msgs.msg import Imu
from pymavlink import mavutil
import math

# CHANGE THIS if BlueOS IP is different. Typical BlueOS default: 192.168.2.2:14550
MAVLINK_URL = "udp:192.168.2.2:14550"

def main():
    rospy.init_node('imu_bridge', anonymous=True)
    imu_pub = rospy.Publisher('/rov/imu', Imu, queue_size=10)

    rospy.loginfo("Connecting to MAVLink: %s", MAVLINK_URL)
    master = mavutil.mavlink_connection(MAVLINK_URL, autoreconnect=True, source_system=255)

    # Wait for heartbeat to ensure connection established
    rospy.loginfo("Waiting for heartbeat...")
    try:
        master.wait_heartbeat(timeout=10)
        rospy.loginfo("Heartbeat from system (type %d, autopilot %d)", master.target_system, master.target_component)
    except Exception as e:
        rospy.logwarn("No heartbeat: %s", e)

    rate = rospy.Rate(50)  # publish up to 50 Hz
    while not rospy.is_shutdown():
        # Try to get HIGHRES_IMU first for accel/gyro/mag
        msg = master.recv_match(type=['HIGHRES_IMU','ATTITUDE'], blocking=True, timeout=1)
        if msg is None:
            rate.sleep()
            continue
        imu_msg = Imu()
        imu_msg.header.stamp = rospy.Time.now()
        imu_msg.header.frame_id = "rov_base_link"

        if msg.get_type() == 'HIGHRES_IMU':
            # HIGHRES_IMU fields: time_usec, xacc, yacc, zacc, xgyro, ygyro, zgyro, xmag, ymag, zmag, abs_pressure, diff_pressure, pressure_alt, temperature
            imu_msg.linear_acceleration.x = float(msg.xacc)
            imu_msg.linear_acceleration.y = float(msg.yacc)
            imu_msg.linear_acceleration.z = float(msg.zacc)
            imu_msg.angular_velocity.x = float(msg.xgyro)
            imu_msg.angular_velocity.y = float(msg.ygyro)
            imu_msg.angular_velocity.z = float(msg.zgyro)
            # orientation unknown: leave zeros and set covariance to -1 to indicate unknown by convention
            imu_msg.orientation_covariance[0] = -1.0
        elif msg.get_type() == 'ATTITUDE':
            # ATTITUDE provides roll/pitch/yaw rates and angles, but not linear accel
            # Fill angular velocity with rollspeed/pitchspeed/yawspeed
            imu_msg.angular_velocity.x = float(msg.rollspeed)
            imu_msg.angular_velocity.y = float(msg.pitchspeed)
            imu_msg.angular_velocity.z = float(msg.yawspeed)
            imu_msg.orientation_covariance[0] = -1.0
        else:
            continue

        try:
            imu_pub.publish(imu_msg)
        except rospy.ROSException as e:
            rospy.logwarn("Publish failed: %s", e)

        rate.sleep()

if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass