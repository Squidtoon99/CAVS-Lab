#ifndef rosencode_UDP_RECEIVER_HPP
#define rosencode_UDP_RECEIVER_HPP

#include <rclcpp/rclcpp.hpp>

// Windows vs Linux Socket Abstraction Layer
#ifdef _WIN32
  #ifndef WIN32_LEAN_AND_MEAN
    #define WIN32_LEAN_AND_MEAN
  #endif
  #include <winsock2.h>
  #include <ws2tcpip.h>

  // Link Windows Socket library
  #pragma comment(lib, "ws2_32.lib")

  using socket_t = SOCKET;
  #define CLOSE_SOCKET closesocket
#else
  #include <sys/socket.h>
  #include <sys/types.h>
  #include <arpa/inet.h>
  #include <netinet/in.h>
  #include <unistd.h>

  using socket_t = int;
  #define CLOSE_SOCKET close
  #ifndef INVALID_SOCKET
    #define INVALID_SOCKET (-1)
  #endif
  #ifndef SOCKET_ERROR
    #define SOCKET_ERROR (-1)
  #endif
#endif

#define RTMAPS_PLATFORM
#define DSA_PACK_STRUCTURES

#include "dsa_gen_DirectCommandTest.h"

#define rosencode_DSA_STRUCTURE_SIZE 17
#define rosencode_DSA_BUS_SIZE (rosencode_DSA_STRUCTURE_SIZE + DSA_HEADER_PAYLOAD_OFFSET)
#define rosencode_DSA_HASHCODE -1395780932

typedef DirectCommandTest_Wrapper bus_struct_wrapper;

class rosencodeUdpReceiver {
 private:
  struct sockaddr_in servaddr_;
  socket_t socket_ = INVALID_SOCKET; // Cross-platform socket handle
  int port_;
  uint8_t counter_ = 0;
  rclcpp::Node::SharedPtr node_;

 public:
  rosencodeUdpReceiver(int port, rclcpp::Node::SharedPtr node);
  ~rosencodeUdpReceiver();

  socket_t get_socket();
  int get_port();
  void receive(bus_struct_wrapper& rtmaps_bus_wrapper, int& error_code);
};

#endif