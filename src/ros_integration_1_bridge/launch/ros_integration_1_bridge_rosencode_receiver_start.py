import os

import launch
import launch_ros.actions
import ament_index_python

package_prefix = ament_index_python.get_package_share_directory('ros_integration_1_bridge')
config = os.path.join(package_prefix, 'params', 'params.yaml')

def generate_launch_description():
    return launch.LaunchDescription([
        launch_ros.actions.Node(
            package="ros_integration_1_bridge",
            executable="ros_integration_1_bridge_rosencode_receiver_node",
            name="ros_integration_1_rosencode_bridge_receiver_node",
            output="screen",
            parameters=[config])
    ])
