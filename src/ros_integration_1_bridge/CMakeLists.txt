cmake_minimum_required(VERSION 3.5)
project(ros_integration_1_bridge)
set(CMAKE_WINDOWS_EXPORT_ALL_SYMBOLS ON)

# Default to C99
if(NOT CMAKE_C_STANDARD)
  set(CMAKE_C_STANDARD 99)
endif()

# Default to C++14
if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 14)
endif()

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

if($ENV{ROS_DISTRO} STREQUAL "crystal")
  add_definitions(-DROS_CRYSTAL)
elseif($ENV{ROS_DISTRO} STREQUAL "dashing")
  add_definitions(-DROS_DASHING)
elseif($ENV{ROS_DISTRO} STREQUAL "eloquent")
  add_definitions(-DROS_ELOQUENT)
elseif($ENV{ROS_DISTRO} STREQUAL "foxy")
  add_definitions(-DROS_FOXY)
elseif($ENV{ROS_DISTRO} STREQUAL "galactic")
  add_definitions(-DROS_GALACTIC)
elseif($ENV{ROS_DISTRO} STREQUAL "humble")
  add_definitions(-DROS_HUMBLE)
elseif($ENV{ROS_DISTRO} STREQUAL "iron")
  add_definitions(-DROS_IRON)
elseif($ENV{ROS_DISTRO} STREQUAL "jazzy")
  add_definitions(-DROS_JAZZY)
elseif($ENV{ROS_DISTRO} STREQUAL "kilted")
  add_definitions(-DROS_KILTED)
else()
  message(FATAL_ERROR "Unsupported rosversion: $ENV{ROS_DISTRO}.")
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(std_msgs REQUIRED)
find_package(builtin_interfaces REQUIRED)
find_package(rosidl_default_generators REQUIRED)
find_package(diagnostic_msgs REQUIRED)
find_package(trajectory_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(action_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(drive_msgs REQUIRED)
find_package(shape_msgs REQUIRED)
find_package(stereo_msgs REQUIRED)

include_directories(include)

add_library(rosencode_udp_receiver SHARED src/rosencode_udp_receiver.cpp)
target_compile_definitions(rosencode_udp_receiver PRIVATE "COMPOSITION_BUILDING_DLL")

if($ENV{ROS_DISTRO} STREQUAL "kilted")
  	target_link_libraries(rosencode_udp_receiver rclcpp::rclcpp)
else()	
	ament_target_dependencies(rosencode_udp_receiver "rclcpp")
endif()


add_executable(ros_integration_1_bridge_rosencode_receiver_node src/ros_integration_1_bridge_rosencode_receiver_node.cpp)

if($ENV{ROS_DISTRO} STREQUAL "kilted")
	target_link_libraries(ros_integration_1_bridge_rosencode_receiver_node ${drive_msgs_TARGETS} rclcpp::rclcpp ${builtin_interfaces_TARGETS})
else()
	ament_target_dependencies(ros_integration_1_bridge_rosencode_receiver_node "drive_msgs" "rclcpp" "builtin_interfaces")
endif()
target_link_libraries(ros_integration_1_bridge_rosencode_receiver_node rosencode_udp_receiver)




install(TARGETS
	rosencode_udp_receiver
	ARCHIVE DESTINATION lib
	LIBRARY DESTINATION lib
	RUNTIME DESTINATION bin
)

install(TARGETS 
  ros_integration_1_bridge_rosencode_receiver_node
  DESTINATION lib/${PROJECT_NAME}
)


# Install launch/params files.
install(DIRECTORY
  launch
  params
  DESTINATION share/${PROJECT_NAME}/
)

ament_export_dependencies(rosidl_default_runtime)
ament_package()
