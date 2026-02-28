#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy, HistoryPolicy
from geometry_msgs.msg import PoseStamped
import transforms3d as tf3d
import math


class AttitudeConverter(Node):
    def __init__(self):
        super().__init__('attitude_converter')
        
        # Match MAVROS QoS (BEST_EFFORT)
        qos_profile = QoSProfile(
            reliability=ReliabilityPolicy.BEST_EFFORT,
            history=HistoryPolicy.KEEP_LAST,
            depth=10
        )
        
        self.subscription = self.create_subscription(
            PoseStamped,
            '/mavros/local_position/pose',
            self.pose_callback,
            qos_profile
        )
        self.get_logger().info('Attitude converter started!')

    def pose_callback(self, msg):
        q = [msg.pose.orientation.x, msg.pose.orientation.y, 
             msg.pose.orientation.z, msg.pose.orientation.w]
        
        try:
            mat = tf3d.quaternions.quat2mat(q)
            roll, pitch, yaw = tf3d.euler.mat2euler(mat, 'sxyz')
            
            roll_deg = math.degrees(roll)
            pitch_deg = math.degrees(pitch)
            yaw_deg = math.degrees(yaw)
            
            self.get_logger().info(
                f'Roll: {roll_deg:7.2f}°  |  Pitch: {pitch_deg:7.2f}°  |  Yaw: {yaw_deg:7.2f}° | '
                f'Depth: {msg.pose.position.z:7.2f}m'
            )
        except Exception as e:
            self.get_logger().error(f'Error: {e}')


def main():
    rclpy.init()
    node = AttitudeConverter()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        print('\nShutdown.')
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
