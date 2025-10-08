#!/usr/bin/env python
import rospy
import actionlib
from assignment_2_2024.msg import PlanningAction, PlanningGoal
from nav_msgs.msg import Odometry
from geometry_msgs.msg import Point, PoseStamped
from nav_pkg.msg import robot_pos_vel
from nav_pkg.srv import SendTarget, SendTargetResponse
from std_srvs.srv import SetBool, SetBoolResponse
import threading

# Global variables
_last_target = None
_last_target_lock = threading.Lock()


class ActionClientNode:
    def __init__(self):
        rospy.init_node('action_client_node')
	
	# Action client
        self.client = actionlib.SimpleActionClient('/reaching_goal', PlanningAction)
        rospy.loginfo("Waiting for action server '/reaching_goal'...")
        self.client.wait_for_server()
        rospy.loginfo("Connected to '/reaching_goal' action server.")
	
	# Publishers
        self.robot_state_pub = rospy.Publisher('/robot_state', robot_pos_vel, queue_size=10)
        self.last_target_pub = rospy.Publisher('/last_target', Point, queue_size=1, latch=True)

	# Subscribers
        rospy.Subscriber('/odom', Odometry, self.odom_callback)

	# Services
        self.set_target_srv = rospy.Service('/set_target', SendTarget, self.set_target_callback)
        self.cancel_srv = rospy.Service('/cancel_target', SetBool, self.cancel_callback)
	
	# State storage
        self.current_odom = None
        self.current_twist = None

        rospy.loginfo("action_client_node is ready. Use /set_target to send goals.")

    def odom_callback(self, msg):
        """Read odometry and publish custom RobotState."""
        self.current_odom = msg.pose.pose.position
        self.current_twist = msg.twist.twist

        rs = robot_pos_vel()
        rs.x = self.current_odom.x
        rs.y = self.current_odom.y
        rs.vel_x = self.current_twist.linear.x
        rs.vel_y = self.current_twist.linear.y
        self.robot_state_pub.publish(rs)

    def set_target_callback(self, req):
        """Called when /set_target service is invoked."""
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
        """Called when /cancel_target service is invoked."""
        if req.data:
            rospy.loginfo("Cancelling current goal...")
            self.client.cancel_all_goals()
            return SetBoolResponse(success=True, message="Goal cancelled.")
        else:
            return SetBoolResponse(success=True, message="No cancellation requested.")

    # Action callback
    def active_cb(self):
        rospy.loginfo("Goal is now active.")

    def feedback_cb(self, feedback):
        rospy.loginfo_throttle(1.0, f"Feedback: {feedback.stat}")

    def done_cb(self, state, result):
        rospy.loginfo(f"Goal finished with state [{state}]")

    def spin(self):
        rospy.spin()


if __name__ == '__main__':
    node = ActionClientNode()
    node.spin()
