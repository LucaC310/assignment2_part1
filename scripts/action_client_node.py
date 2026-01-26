#!/usr/bin/env python
import rospy
import actionlib
from assignment_2_2024.msg import PlanningAction, PlanningGoal
from nav_msgs.msg import Odometry, LaserScan
from geometry_msgs.msg import Point, PoseStamped
from nav_pkg.msg import robot_pos_vel
from nav_pkg.srv import SendTarget, SendTargetResponse
from std_srvs.srv import SetBool, SetBoolResponse
import threading

# Global variables
_last_target = None
_last_target_lock = threading.Lock()
_goals_reached = 0
_goals_cancelled = 0
_goals_lock = threading.Lock()


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
        self.closest_obs_pub = rospy.Publisher('/closest_obstacle', Point, queue_size=10)  # x=distance, y=angle
        
        # Subscribers
        rospy.Subscriber('/odom', Odometry, self.odom_callback)
        rospy.Subscriber('/scan', LaserScan, self.laser_callback)  # New subscriber for obstacles
        
        # Services
        self.set_target_srv = rospy.Service('/set_target', SendTarget, self.set_target_callback)
        self.cancel_srv = rospy.Service('/cancel_target', SetBool, self.cancel_callback)
        self.stats_srv = rospy.Service('/goal_stats', SetBool, self.stats_callback)  # New service
        
        # State storage
        self.current_odom = None
        self.current_twist = None

        rospy.loginfo("action_client_node is ready. Use /set_target to send goals.")

    #Odom callback
    def odom_callback(self, msg):
        self.current_odom = msg.pose.pose.position
        self.current_twist = msg.twist.twist

        rs = robot_pos_vel()
        rs.x = self.current_odom.x
        rs.y = self.current_odom.y
        rs.vel_x = self.current_twist.linear.x
        rs.vel_y = self.current_twist.linear.y
        self.robot_state_pub.publish(rs)

    # Laser scan callback
    def laser_callback(self, msg: LaserScan):
        """Publish distance and direction of the closest obstacle."""
        if not msg.ranges:
            return

        min_distance = float('inf')
        min_angle = 0.0
        for i, r in enumerate(msg.ranges):
            if msg.range_min < r < min_distance:
                min_distance = r
                min_angle = msg.angle_min + i * msg.angle_increment

        closest = Point()
        closest.x = min_distance
        closest.y = min_angle
        closest.z = 0.0
        self.closest_obs_pub.publish(closest)

    #Set target callback
    def set_target_callback(self, req):
        global _last_target, _last_target_lock

        rospy.loginfo(f"New target received: x={req.x:.2f}, y={req.y:.2f}")

        goal = PlanningGoal()
        goal.target_pose = PoseStamped()
        goal.target_pose.pose.position.x = req.x
        goal.target_pose.pose.position.y = req.y
        goal.target_pose.pose.position.z = 0.0

        with _last_target_lock:
            _last_target = Point(req.x, req.y, 0.0)
            self.last_target_pub.publish(_last_target)

        self.client.send_goal(goal,
                              done_cb=self.done_cb,
                              active_cb=self.active_cb,
                              feedback_cb=self.feedback_cb)
        return SendTargetResponse(accepted=True)

    #Cancel callback
    def cancel_callback(self, req):
        global _goals_cancelled, _goals_lock

        if req.data:
            rospy.loginfo("Cancelling current goal...")
            self.client.cancel_all_goals()
            with _goals_lock:
                _goals_cancelled += 1
            return SetBoolResponse(success=True, message="Goal cancelled.")
        else:
            return SetBoolResponse(success=True, message="No cancellation requested.")

    #Goal stats service    
    def stats_callback(self, req):
        global _goals_reached, _goals_cancelled, _goals_lock
        with _goals_lock:
            message = f"Goals reached: {_goals_reached}, Goals cancelled: {_goals_cancelled}"
        rospy.loginfo(message)
        return SetBoolResponse(success=True, message=message)

    #Action callbacks
    def active_cb(self):
        rospy.loginfo("Goal is now active.")

    def feedback_cb(self, feedback):
        rospy.loginfo_throttle(1.0, f"Feedback: {feedback.stat}")

    def done_cb(self, state, result):
        global _goals_reached, _goals_lock
        rospy.loginfo(f"Goal finished with state [{state}]")
        if state == 3:  # 3 = SUCCEEDED
            with _goals_lock:
                _goals_reached += 1

    # Spin node
    def spin(self):
        rospy.spin()


if __name__ == '__main__':
    node = ActionClientNode()
    node.spin()

