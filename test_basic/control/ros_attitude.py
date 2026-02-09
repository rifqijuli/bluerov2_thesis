#!/usr/bin/env python3
import rclpy
from rclpy.node import Node
from geometry_msgs.msg import PoseStamped
import transforms3d as tf3d  # ← New import
import math
import time

class AttitudeController(Node):
    def __init__(self):
        super().__init__('attitude_controller')
        self.publisher = self.create_publisher(PoseStamped, '/mavros/setpoint_raw/attitude', 10)
        self.get_logger().info('Attitude controller ready!')

    def set_target_attitude(self, roll_deg=0, pitch_deg=0, yaw_deg=0):
        # Convert to radians
        roll, pitch, yaw = map(math.radians, [roll_deg, pitch_deg, yaw_deg])
        
        # transforms3d quaternion (x,y,z,w order)
        q = tf3d.euler.euler2quat(roll, pitch, yaw, axes='sxyz')
        
        msg = PoseStamped()
        msg.header.stamp = self.get_clock().now().to_msg()
        msg.header.frame_id = 'base_link'
        msg.pose.orientation.x = q[0]
        msg.pose.orientation.y = q[1]
        msg.pose.orientation.z = q[2]
        msg.pose.orientation.w = q[3]
        
        self.publisher.publish(msg)
        self.get_logger().info(f'Sent attitude: yaw={yaw_deg:.1f}°')

def main():
    rclpy.init()
    node = AttitudeController()
    
    roll_angle = pitch_angle = 0
    
    # Spin like pymavlink example
    for yaw_angle in range(0, 500, 10):
        node.set_target_attitude(roll_angle, pitch_angle, yaw_angle)
        rclpy.spin_once(node, timeout_sec=0.1)
        time.sleep(1)
    
    # Spin back
    for yaw_angle in range(500, 0, -30):
        node.set_target_attitude(roll_angle, pitch_angle, yaw_angle)
        rclpy.spin_once(node, timeout_sec=0.1)
        time.sleep(1)
    
    node.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()