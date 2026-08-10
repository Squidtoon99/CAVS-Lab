#ifndef UTILS_HPP
#define UTILS_HPP

#include <rclcpp/rclcpp.hpp>

rclcpp::Parameter set_parameter(rclcpp::Node::SharedPtr node, std::string name, rclcpp::Parameter default_param) {
  rclcpp::Parameter param;
#ifdef ROS_CRYSTAL
  node->get_parameter_or(name, param, default_param);
#endif
#if defined(ROS_DASHING) || defined (ROS_ELOQUENT) || defined (ROS_FOXY)
  if(!node->has_parameter(name)) node->declare_parameter(name);
  node->get_parameter_or(name, param, default_param);
#endif
#if defined(ROS_GALACTIC) || defined (ROS_HUMBLE) || defined (ROS_IRON) || defined (ROS_JAZZY) || defined (ROS_KILTED)
  rcl_interfaces::msg::ParameterDescriptor descriptor;
  descriptor.dynamic_typing = true;
  if(!node->has_parameter(name)) node->declare_parameter(name, rclcpp::ParameterValue{}, descriptor);
  node->get_parameter_or(name, param, default_param);
#endif
  return param;
}

#endif
