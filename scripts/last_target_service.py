#!/usr/bin/env python
import rospy
from nav_pkg.srv import GetLastTarget, GetLastTargetResponse
from geometry_msgs.msg import Point

_last_target = None

def last_target_callback(msg):
    """Receive last target published by action_client_node."""
    global _last_target
    _last_target = msg

def handle_get_last_target(req):
    """Return the last target sent by the user."""
    global _last_target
    if _last_target is None:
        rospy.logwarn("No target has been set yet; returning (0,0)")
        return GetLastTargetResponse(x=0.0, y=0.0)
    else:
        return GetLastTargetResponse(x=_last_target.x, y=_last_target.y)

def main():
    rospy.init_node('last_target_service_node')
    rospy.Subscriber('/last_target', Point, last_target_callback)
    rospy.Service('/get_last_target', GetLastTarget, handle_get_last_target)
    rospy.loginfo("Service /get_last_target is ready.")
    rospy.spin()

if __name__ == '__main__':
    main()
