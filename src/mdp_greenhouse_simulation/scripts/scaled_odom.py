#!/usr/bin/env python3
"""Publish intentionally scaled odometry for Cartographer testing."""

import math

import rclpy
from geometry_msgs.msg import TransformStamped
from nav_msgs.msg import Odometry
from rclpy.node import Node
from tf2_ros import TransformBroadcaster


def yaw_from_quaternion(q):
    siny_cosp = 2.0 * (q.w * q.z + q.x * q.y)
    cosy_cosp = 1.0 - 2.0 * (q.y * q.y + q.z * q.z)
    return math.atan2(siny_cosp, cosy_cosp)


def quaternion_from_yaw(yaw):
    half = 0.5 * yaw
    return 0.0, 0.0, math.sin(half), math.cos(half)


class ScaledOdom(Node):
    def __init__(self):
        super().__init__('scaled_odom')
        self.declare_parameter('scale', 3.0)
        self.declare_parameter('input_topic', '/odom')
        self.declare_parameter('output_topic', '/bad_odom')
        self.declare_parameter('output_frame', 'bad_odom')
        self.declare_parameter('child_frame', 'base_link')
        self.declare_parameter('publish_tf', True)

        self.scale = float(self.get_parameter('scale').value)
        self.output_frame = self.get_parameter('output_frame').value
        self.child_frame = self.get_parameter('child_frame').value
        self.publish_tf = bool(self.get_parameter('publish_tf').value)

        input_topic = self.get_parameter('input_topic').value
        output_topic = self.get_parameter('output_topic').value

        self.publisher = self.create_publisher(Odometry, output_topic, 10)
        self.tf_broadcaster = TransformBroadcaster(self)
        self.subscription = self.create_subscription(
            Odometry,
            input_topic,
            self._on_odom,
            10,
        )
        self.get_logger().info(
            f'scaling odom from {input_topic} to {output_topic}: '
            f'frame={self.output_frame}, child={self.child_frame}, scale={self.scale}'
        )

    def _on_odom(self, msg):
        scaled = Odometry()
        scaled.header = msg.header
        scaled.header.frame_id = self.output_frame
        scaled.child_frame_id = self.child_frame

        scaled.pose = msg.pose
        scaled.pose.pose.position.x = msg.pose.pose.position.x * self.scale
        scaled.pose.pose.position.y = msg.pose.pose.position.y * self.scale
        scaled.pose.pose.position.z = msg.pose.pose.position.z

        yaw = yaw_from_quaternion(msg.pose.pose.orientation)
        qx, qy, qz, qw = quaternion_from_yaw(yaw * self.scale)
        scaled.pose.pose.orientation.x = qx
        scaled.pose.pose.orientation.y = qy
        scaled.pose.pose.orientation.z = qz
        scaled.pose.pose.orientation.w = qw

        scaled.twist = msg.twist
        scaled.twist.twist.linear.x = msg.twist.twist.linear.x * self.scale
        scaled.twist.twist.linear.y = msg.twist.twist.linear.y * self.scale
        scaled.twist.twist.angular.z = msg.twist.twist.angular.z * self.scale

        self.publisher.publish(scaled)

        if self.publish_tf:
            transform = TransformStamped()
            transform.header = scaled.header
            transform.child_frame_id = self.child_frame
            transform.transform.translation.x = scaled.pose.pose.position.x
            transform.transform.translation.y = scaled.pose.pose.position.y
            transform.transform.translation.z = scaled.pose.pose.position.z
            transform.transform.rotation = scaled.pose.pose.orientation
            self.tf_broadcaster.sendTransform(transform)


def main():
    rclpy.init()
    node = ScaledOdom()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
