# Robot Action Client (ROS)

This repository contains a **ROS package** that implements two main nodes:

- `action_client_node`
- `last_target_service_node`

It works together with the [assignment_2_2024](https://github.com/CarmineD8/assignment_2_2024) package, which provides the **action server** responsible for robot motion control and obstacle avoidance.

## Overview

### Action Client Node

The `action_client_node` implements a ROS **action client** that communicates with the `/reaching_goal` action server.

It allows the user to:

- **Set a new target** position `(x, y)`.
- **Cancel the current target**.
- **Track the progress** of the robot towards its target.

Additionally, this node subscribes to `/odom` to retrieve the robot's position and velocity and publishes this information using a **custom ROS message**.

### Last Target Service Node

The `last_target_service_node` provides a **ROS service** that returns the coordinates of the last target sent by the user.

## Launch

The package provides a launch file named `assignment2.launch`.

Running this launch file will:

- Start the `assignment1.launch` file.
- Launch the `action_client_node` and `last_target_service_node` simultaneously.

## Documentation

The Python source code is documented using **Sphinx**, including the main classes, functions, methods, and ROS callbacks.

The documentation includes:

- Automatically generated API documentation using `sphinx.ext.autodoc`.
- Source code references using `sphinx.ext.viewcode`.
- Dedicated pages displaying the Python source files.

### Requirements

The documentation requires Python 3 and the following packages:

```bash
python3 -m pip install sphinx sphinx-rtd-theme breathe
```

### Build the Documentation

From the root directory of the `nav_pkg` package, run:

```bash
python3 -m sphinx -b html source build/html
```

To perform a complete build with strict warning checks:

```bash
python3 -m sphinx -E -a -b html -n -W --keep-going source build/html
```

### View the Documentation

After building, open:

```text
build/html/index.html
```

The repository also includes pre-generated HTML documentation in the `docs/` directory.
