#!/usr/bin/env python3
import rospy
from sensor_msgs.msg import Imu

def imu_cb(msg):
    # Print a compact summary: timestamp, lin accel (norm), ang vel (norm)
    la = msg.linear_acceleration
    av = msg.angular_velocity
    lin_norm = (la.x**2 + la.y**2 + la.z**2)**0.5
    ang_norm = (av.x**2 + av.y**2 + av.z**2)**0.5
    rospy.loginfo_throttle(1, "IMU: lin_a=%.3f m/s^2 ang_v=%.3f rad/s", lin_norm, ang_norm)

def main():
    rospy.init_node('imu_consumer', anonymous=True)
    rospy.Subscriber('/rov/imu', Imu, imu_cb, queue_size=10)
    rospy.loginfo("imu_consumer: listening to /rov/imu")
    rospy.spin()

if __name__ == '__main__':
    main()