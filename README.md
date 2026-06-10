# CAVS-Lab

## Goal
The overall objective for this lab is to create a testbed for autonomous vehicle control. That is, it should be possible to observe the effects of a simulated autonomous vehicle on a real world equivalent "digital traffic twin." We aim to accomplish this by mirroring the output (vehicle commands/trajectories) from a dSpace SCALEXIO onto a scaled physical RC car (a [Waveshare PiRace Pro AI](https://www.waveshare.com/piracer-pro-ai-kit.htm)) in a lab environment.

## Tech Stack
We make use of the following technologies, which you may find helpful to familiarize yourself with:
- Python 3 - Most of our programming is done in Python
- [ROS2 (Jazzy)](https://docs.ros.org/en/jazzy/index.html#) - Our system is designed as a network of ROS nodes; we use Jazzy primarily, though knowledge is largely transferrable between other ROS2 versions.
- C++, CMake, & Colcon - A passing familiarity with these is helpful, as they are used as part of the build system for some of our ROS nodes.
- Matlab & Simulink - You don't need to be proficient in these, but being able to at least read and understand basic Simulink code will be helpful. Most relevant to the software team will be the [ROS Interface blockset](https://www.dspace.com/en/inc/home/products/sw/impsw/dspace_interface_blockset_ros.cfm).
- Git - Basic knowledge of how to use a VCS properly

The single most important thing to familiarize yourself with if you're coming into the project is ROS2, as that is essentially the backbone of how our system runs. If you do not understand ROS, you will be lost trying to understand how everything works and interacts with each other. To that end, I would recommend reading at least the Beginner section (both for CLI tools and client libraries) on the [tutorial](https://docs.ros.org/en/jazzy/Tutorials.html) page.

Beyond that, a decent understanding of the basics of networking can prove useful, as many of the issues we run into originate from networking problems. You do not need to be an expert, but a basic understanding of how IPv4 ranges work and being able to pull up Wireshark in order to inspect network traffic will make your life a lot easier.

## Project Structure & Architecture
The code for the project is stored under the `src/` directory, where each subfolder is a separate ROS node. The primary code responsible for running on each ROS node is stored under the subfolder with the same name as the ROS node (eg, for the `ips_publisher` node, the code is stored under the `ips_publisher/ips_publisher/` directory).

Our current set of ROS nodes are as follows:
- `ips_publisher` - Runs the Internal Positioning System (IPS) responsible for identifying and broadcasting the positions of AprilTags within the lab environment.
- `gui_visualizer` - A GUI interface for tracking the position, movement, and detection status of each AprilTag.
- `ips_interfaces` - The `msgs` subfolder stores the ROS message formats that this system sends.

As a final note, ROS is primarily a peer-to-peer publisher/subscriber architecture. However, peer discovery is done through multicast, which is blocked entirely on UTD networks as a security measure. Therefore, we instead use a brokered connection via a central [discovery server](https://docs.ros.org/en/jazzy/Tutorials/Advanced/Discovery-Server/Discovery-Server.html) for finding peers.
