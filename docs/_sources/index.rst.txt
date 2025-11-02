.. nav_pkg documentation master file

Welcome to nav_pkg's documentation!
===================================

The **nav_pkg** package provides ROS nodes and services for managing
navigation tasks, including goal handling, target tracking, and robot state
monitoring.

Contents
--------

.. toctree::
   :maxdepth: 2
   :caption: Package Modules
   
   action_client_node_source
   last_target_service_source

Package Overview
----------------

- **action_client_node**
  
  A ROS action client node that communicates with the `/reaching_goal` action server.
  It allows users to send or cancel navigation targets and publishes the robot's
  current position, velocity, and last target.

- **last_target_service**
  
  A ROS service node that provides the `/get_last_target` service, returning
  the most recently received navigation target from the `/last_target` topic.

Module Documentation
--------------------

**action_client_node**

.. automodule:: nav_pkg.scripts.action_client_node
   :members:
   :undoc-members:
   :show-inheritance:

**last_target_service**

.. automodule:: nav_pkg.scripts.last_target_service
   :members:
   :undoc-members:
   :show-inheritance:

Full Source Code
----------------

- `action_client_node.py source code <action_client_node_source.html>`_
- `last_target_service.py source code <last_target_service_source.html>`_

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

