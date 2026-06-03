import time
import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy

# Import your custom message
from ips_interfaces.msg import VehicleObservation

class AprilTagTestSubscriber(Node):
    def __init__(self):
        super().__init__('apriltag_test_subscriber')

        # 1. Parameter to match the publisher's topic generation
        self.declare_parameter('system.number_vehicles', 20)
        self.number_vehicles = self.get_parameter('system.number_vehicles').value

        # 2. MATCH THE PUBLISHER'S QoS PROFILE
        # This is critical. A RELIABLE subscriber cannot hear a BEST_EFFORT publisher.
        qos = QoSProfile(
            depth=10, 
            reliability=ReliabilityPolicy.BEST_EFFORT
        )

        self.subscribers =[]
        self.last_print_times = {}

        # 3. Create a subscriber for every possible vehicle topic
        for i in range(0, self.number_vehicles + 1):
            topic_name = f'vehicle_{i}/vehicleObservation'
            
            sub = self.create_subscription(
                VehicleObservation,
                topic_name,
                self.listener_callback,
                qos
            )
            self.subscribers.append(sub)

        self.get_logger().info(f"Test Subscriber initialized. Listening on {self.number_vehicles} vehicle topics...")

    def listener_callback(self, msg: VehicleObservation):
        vehicle_id = msg.vehicle_id
        current_time = time.time()

        # Rate Limiter: Only log once per second per vehicle to avoid terminal spam
        if vehicle_id not in self.last_print_times or (current_time - self.last_print_times[vehicle_id]) >= 1.0:
            self.last_print_times[vehicle_id] = current_time

            # Calculate transport & processing latency
            now = self.get_clock().now()
            stamp_sec = msg.header.stamp.sec + (msg.header.stamp.nanosec * 1e-9)
            now_sec = now.nanoseconds * 1e-9
            latency_ms = (now_sec - stamp_sec) * 1000.0

            # Extract Pose Data
            pos = msg.pose.position
            quat = msg.pose.orientation

            # Format the output clearly
            log_output = (
                f"\n--- Vehicle {vehicle_id:02d} Observation --- \n"
                f"  Frame ID: {msg.header.frame_id}\n"
                f"  Position: X: {pos.x:.3f}, Y: {pos.y:.3f}, Z: {pos.z:.3f}\n"
                f"  Orientat: X: {quat.x:.3f}, Y: {quat.y:.3f}, Z: {quat.z:.3f}, W: {quat.w:.3f}\n"
                f"  Latency : {latency_ms:.2f} ms\n"
            )
            
            self.get_logger().info(log_output)


def main(args=None):
    rclpy.init(args=args)
    node = AprilTagTestSubscriber()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()