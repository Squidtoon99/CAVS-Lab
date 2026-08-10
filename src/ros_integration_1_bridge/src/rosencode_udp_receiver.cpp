#include <ros_integration_1_bridge/rosencode_udp_receiver.hpp>

// Avoid "using namespace std;" to prevent std::bind namespace collisions
using std::memset;
using std::memcpy;

rosencodeUdpReceiver::rosencodeUdpReceiver(int port, rclcpp::Node::SharedPtr node) : port_(port), node_(node) {
#ifdef _WIN32
  // Initialize Winsock library on Windows
  WSADATA wsaData;
  if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0) {
    RCLCPP_ERROR(node_->get_logger(), "WSAStartup failed.");
    exit(-1);
  }
#endif

  // Use ::socket to explicitly call the global socket function
  socket_ = ::socket(AF_INET, SOCK_DGRAM, 0);
  
  if (socket_ == INVALID_SOCKET) {
    RCLCPP_ERROR(node_->get_logger(), "Socket creation failed.");
#ifdef _WIN32
    WSACleanup();
#endif
    exit(-1);
  }
  RCLCPP_INFO(node_->get_logger(), "Successfully created socket: %d", static_cast<int>(socket_));
  RCLCPP_INFO(node_->get_logger(), "Listening on port: %d", port_);

  memset(&servaddr_, 0, sizeof(servaddr_));

  // Filling server information
  servaddr_.sin_family = AF_INET;  // IPv4
  servaddr_.sin_addr.s_addr = INADDR_ANY;
  servaddr_.sin_port = htons(port_);

  // FIX: Use ::bind to explicitly call the global socket function, NOT std::bind
  if (::bind(socket_, (const struct sockaddr *)&servaddr_, sizeof(sockaddr_in)) == SOCKET_ERROR) {
    RCLCPP_ERROR(node_->get_logger(), "Binding socket failed.");
    CLOSE_SOCKET(socket_);
#ifdef _WIN32
    WSACleanup();
#endif
    exit(-1);
  }
  RCLCPP_INFO(node_->get_logger(), "Successfully bound to socket: %d", static_cast<int>(socket_));
}

rosencodeUdpReceiver::~rosencodeUdpReceiver() { 
  if (socket_ != INVALID_SOCKET) {
    CLOSE_SOCKET(socket_);
    socket_ = INVALID_SOCKET;
  }
#ifdef _WIN32
  WSACleanup();
#endif
}

void rosencodeUdpReceiver::receive(bus_struct_wrapper& rtmaps_bus_wrapper, int& error_code) {
  char buffer[sizeof(bus_struct_wrapper)];

  // Use ::recv to explicitly call the global socket function
  int length = ::recv(socket_, buffer, sizeof(buffer), 0);
  if (length < 0) {
    RCLCPP_ERROR(node_->get_logger(), "No Data Received.");
    error_code = -1;
  }
  else if (length != rosencode_DSA_BUS_SIZE) {
    RCLCPP_ERROR(node_->get_logger(), "Number of received bytes %d do not match the expected byte size %d.", length, rosencode_DSA_BUS_SIZE);
    error_code = -1;
  }
  else {
    memcpy(&rtmaps_bus_wrapper, buffer, sizeof(rtmaps_bus_wrapper));
    if(rtmaps_bus_wrapper.crc != rosencode_DSA_HASHCODE) {
      RCLCPP_ERROR(node_->get_logger(), "Received Hashcode %d does not match expected Hashcode %d.", rtmaps_bus_wrapper.crc, rosencode_DSA_HASHCODE);
      error_code = -1;
    } else if (rtmaps_bus_wrapper.counter != counter_) {
      RCLCPP_WARN(node_->get_logger(), "Received counter %d does not match the expected counter %d. A packet may have disappeared.", rtmaps_bus_wrapper.counter, counter_);
    } else {
      error_code = 0;
    }
    counter_ = rtmaps_bus_wrapper.counter + 1;
  }
}

socket_t rosencodeUdpReceiver::get_socket() { return socket_; }

int rosencodeUdpReceiver::get_port() { return port_; }