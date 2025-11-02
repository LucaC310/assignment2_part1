#!/usr/bin/env python
"""
ROS Node: last_target_service_node
==================================

This node provides a service `/get_last_target` that returns the last target
position received from the `/last_target` topic.

The service is useful for other nodes that need to know the most recent target
set by the user or another node (e.g., an action client).

**Published Topics**
    None

**Subscribed Topics**
    - `/last_target` (`geometry_msgs/Point`): Receives the last target position.

**Services**
    - `/get_last_target` (`nav_pkg/GetLastTarget`): Returns the last known target position.

"""

import rospy
from nav_pkg.srv import GetLastTarget, GetLastTargetResponse
from geometry_msgs.msg import Point

_last_target = None


def last_target_callback(msg):
    """
    Callback for the `/last_target` topic.

    This function updates the global variable `_last_target` whenever a new
    `geometry_msgs/Point` message is received.

    Parameters
    ----------
    msg : geometry_msgs.msg.Point
        The latest target position published by the `action_client_node`.
    """
    global _last_target
    _last_target = msg


def handle_get_last_target(req):
    """
    Handle service requests to `/get_last_target`.

    Returns the most recent target position received via the `/last_target`
    topic. If no target has been received yet, it returns `(0.0, 0.0)` and
    logs a warning.

    Parameters
    ----------
    req : nav_pkg.srv.GetLastTargetRequest
        Empty service request (no parameters).

    Returns
    -------
    nav_pkg.srv.GetLastTargetResponse
        Response containing the `x` and `y` coordinates of the last target.
    """
    global _last_target
    if _last_target is None:
        rospy.logwarn("No target has been set yet; returning (0,0)")
        return GetLastTargetResponse(x=0.0, y=0.0)
    else:
        return GetLastTargetResponse(x=_last_target.x, y=_last_target.y)


def main():
    """
    Initialize and run the `last_target_service_node`.

    This function sets up:
      - A ROS subscriber to `/last_target` to track the last received target.
      - A ROS service `/get_last_target` to provide the stored target on demand.

    The node runs continuously using `rospy.spin()` until shut down.
    """
    rospy.init_node('last_target_service_node')
    rospy.Subscriber('/last_target', Point, last_target_callback)
    rospy.Service('/get_last_target', GetLastTarget, handle_get_last_target)
    rospy.loginfo("Service /get_last_target is ready.")
    rospy.spin()


if __name__ == '__main__':
    main()

