#include <rclcpp/rclcpp.hpp>
#include <rclcpp/time_source.hpp>
#include <ros_integration_1_bridge/rosencode_udp_receiver.hpp>
#include <ros_integration_1_bridge/utils.hpp>
#include <rclcpp/qos.hpp>

// include all custom messages
#include <drive_msgs/msg/direct_command_test.hpp>
using namespace std;

int main(int argc, char** argv) {
  rclcpp::init(argc, argv);

  rclcpp::Node::SharedPtr node = rclcpp::Node::make_shared("ros_integration_1_bridge_rosencode_receiver_node");
  RCLCPP_INFO(node->get_logger(), "Init Node: '%s'", node->get_name());

  // set parameter - cast int64_t to int to fix Warning C4244
  int port = static_cast<int>(set_parameter(node, "port", rclcpp::Parameter("", 11111)).as_int());
  string pub_topic = set_parameter(node, "topic_out", rclcpp::Parameter("", "ds_to_ros")).as_string();

  // FIX: Changed rclcpp::10 to 10
  rclcpp::Publisher<drive_msgs::msg::DirectCommandTest>::SharedPtr pub = 
      node->create_publisher<drive_msgs::msg::DirectCommandTest>(pub_topic, 10);

  rosencodeUdpReceiver udp_receiver = rosencodeUdpReceiver(port, node);

  int error_code;
  bus_struct_wrapper data;

  while (rclcpp::ok()) {
    udp_receiver.receive(data, error_code);
    if(error_code < 0) continue;

    drive_msgs::msg::DirectCommandTest DirectCommandTest_msg;
    DirectCommandTest_msg.vehicle_id= data.payload.vehicle_id;
    DirectCommandTest_msg.motor_throttle= data.payload.motor_throttle;
    DirectCommandTest_msg.steering_servo= data.payload.steering_servo;

    pub->publish(DirectCommandTest_msg);
    rclcpp::spin_some(node);
  }

  rclcpp::shutdown();
  return 0;
}