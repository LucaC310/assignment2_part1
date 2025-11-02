#!/usr/bin/env python
"""
nav_pkg.action_client_node
==========================

A ROS action client node that interfaces with the `/reaching_goal` action server.

This node allows setting and cancelling navigation goals, publishing robot
state (position and velocity), and tracking the last target set.

Author:
    Luca Carpaneto

Version:
    1.0

Date:
    13/10/2025
"""

import rospy
import actionlib
from assignment_2_2024.msg import PlanningAction, PlanningGoal
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Point, PoseStamped
from nav_pkg.msg import robot_pos_vel
from nav_pkg.srv import SendTarget, SendTargetResponse
from std_srvs.srv import SetBool, SetBoolResponse
import threading

#: The most recent target position sent to the action server.
_last_target = None

#: Threading lock to protect access to the global `_last_target`.
_last_target_lock = threading.Lock()


class ActionClientNode:
    """
    A ROS node that acts as an action client to send navigation goals.

    This class handles:
        - Connection to the `/reaching_goal` action server
        - `/set_target` and `/cancel_target` services
        - Publishing robot position, velocity, and last sent target
    """

    def __init__(self):
        """
        Initialize the action client node, publishers, subscribers, and services.
        """
        rospy.init_node('action_client_node')

        #: Action client for communicating with the `/reaching_goal` action server.
        self.client = actionlib.SimpleActionClient('/reaching_goal', PlanningAction)
        rospy.loginfo("Waiting for action server '/reaching_goal'...")
        self.client.wait_for_server()
        rospy.loginfo("Connected to '/reaching_goal' action server.")

        #: Publisher for robot position and velocity.
        self.robot_state_pub = rospy.Publisher('/robot_state', robot_pos_vel, queue_size=10)

        #: Publisher for the last target position.
        self.last_target_pub = rospy.Publisher('/last_target', Point, queue_size=1, latch=True)

        #: Subscriber for odometry data.
        rospy.Subscriber('/odom', Odometry, self.odom_callback)

        #: Service to set a new navigation target.
        self.set_target_srv = rospy.Service('/set_target', SendTarget, self.set_target_callback)

        #: Service to cancel the current navigation goal.
        self.cancel_srv = rospy.Service('/cancel_target', SetBool, self.cancel_callback)

        #: Current odometry position.
        self.current_odom = None

        #: Current velocity (twist).
        self.current_twist = None

        rospy.loginfo("action_client_node is ready. Use /set_target to send goals.")

    def odom_callback(self, msg):
        """
        Handle incoming odometry messages and publish the robot's position and velocity.

        Parameters
        ----------
        msg : nav_msgs.msg.Odometry
            The received odometry message.
        """
        self.current_odom = msg.pose.pose.position
        self.current_twist = msg.twist.twist

        rs = robot_pos_vel()
        rs.x = self.current_odom.x
        rs.y = self.current_odom.y
        rs.vel_x = self.current_twist.linear.x
        rs.vel_y = self.current_twist.linear.y
        self.robot_state_pub.publish(rs)

    def set_target_callback(self, req):
        """
        Handle `/set_target` service calls to send a new navigation goal.

        Parameters
        ----------
        req : nav_pkg.srv.SendTargetRequest
            The service request containing target coordinates.

        Returns
        -------
        nav_pkg.srv.SendTargetResponse
            True if the goal was accepted.
        """
        global _last_target, _last_target_lock

        rospy.loginfo(f"New target received: x={req.x:.2f}, y={req.y:.2f}")

        # Create action goal
        goal = PlanningGoal()
        goal.target_pose = PoseStamped()
        goal.target_pose.pose.position.x = req.x
        goal.target_pose.pose.position.y = req.y
        goal.target_pose.pose.position.z = 0.0

        # Save and publish last target
        with _last_target_lock:
            _last_target = Point(req.x, req.y, 0.0)
            self.last_target_pub.publish(_last_target)

        # Send goal
        self.client.send_goal(goal,
                              done_cb=self.done_cb,
                              active_cb=self.active_cb,
                              feedback_cb=self.feedback_cb)
        return SendTargetResponse(accepted=True)

    def cancel_callback(self, req):
        """
        Handle `/cancel_target` service calls to cancel the current navigation goal.

        Parameters
        ----------
        req : std_srvs.srv.SetBoolRequest
            The service request containing a boolean flag.

        Returns
        -------
        std_srvs.srv.SetBoolResponse
            Result of the cancel operation.
        """
        if req.data:
            rospy.loginfo("Cancelling current goal...")
            self.client.cancel_all_goals()
            return SetBoolResponse(success=True, message="Goal cancelled.")
        else:
            return SetBoolResponse(success=True, message="No cancellation requested.")

    def active_cb(self):
        """Callback executed when the action goal becomes active."""
        rospy.loginfo("Goal is now active.")

    def feedback_cb(self, feedback):
        """
        Callback executed when feedback is received from the action server.

        Parameters
        ----------
        feedback : assignment_2_2024.msg.PlanningFeedback
            The feedback message from the action server.
        """
        rospy.loginfo_throttle(1.0, f"Feedback: {feedback.stat}")

    def done_cb(self, state, result):
        """
        Callback executed when the action goal completes.

        Parameters
        ----------
        state : int
            The final state of the goal.
        result : assignment_2_2024.msg.PlanningResult
            The result message from the action server.
        """
        rospy.loginfo(f"Goal finished with state [{state}]")

    def spin(self):
        """Keep the node alive and responsive."""
        rospy.spin()


if __name__ == '__main__':
    """
    Main entry point for the ROS action client node.
    """
    node = ActionClientNode()
    node.spin()

