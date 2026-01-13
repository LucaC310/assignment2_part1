# Robot Action Client (ROS)

This repository contains a **ROS package** that implements two main nodes:
- `action_client_node`
- `last_target_service_node`

It works together with [assignment_2_2024](https://github.com/CarmineD8/assignment_2_2024) package, which provides the **action server** responsible for robot motion control and obstacle avoidance.

## Overview

### 'action_client_node'

This node implements an **action client** that interacts with the `/reaching_goal` **action server**.
It allows the user to:

- **Set a new target** (x, y) position
- **Cancel the current target**
- **Receive and display feedback from the action server**

Additionally, this node subscribes to `/odom` to read the robot's position and velocity, and publish them as a **custom message**.

### 'last_target_service_node`

This node provides a **ROS service** that returns the coordinates of the **last target** sent by the user.

## Launch

To start the whole simulation, a launch file is provided: `assignment2.launch`.

Running this launch file will:

- Start the `assignment1.launch` file
- Launch the `action_client_node` and 'last_target_service_node' simultaneously
