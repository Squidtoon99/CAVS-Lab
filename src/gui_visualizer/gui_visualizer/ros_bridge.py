"""ROS2 subscriber node spun in a daemon thread; exposes a thread-safe
snapshot of vehicle data for the Qt GUI to poll."""

import math
import threading
import time
from typing import Dict

from PyQt5.QtCore import QObject

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy


from ips_interfaces.msg import VehicleObservation

from .data_model import VehicleState


class ROSBridge(QObject):
    """Bridges ROS2 VehicleObservation topics into a thread-safe dict."""

    def __init__(self, num_vehicles: int = 20, parent=None):
        super().__init__(parent)
        self._lock = threading.Lock()
        self._vehicles: Dict[int, VehicleState] = {}

        # ── ROS node ──
        self._node = Node("vehicle_visualizer_node")
        qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)

        for i in range(0, num_vehicles):
            topic = f"vehicle_{i}/vehicleObservation"
            self._node.create_subscription(
                VehicleObservation,
                topic,
                lambda msg, vid=i: self._on_observation(msg, vid),
                qos,
            )
        self._node.get_logger().info(
            f"Visualizer subscribing to {num_vehicles} vehicle topics."
        )

    def _on_observation(self, msg: VehicleObservation, vehicle_id: int):
        with self._lock:
            if vehicle_id not in self._vehicles:
                self._vehicles[vehicle_id] = VehicleState(vehicle_id=vehicle_id)
            v = self._vehicles[vehicle_id]

            v.position_x = msg.pose.position.x
            v.position_y = msg.pose.position.y

            v.yaw = math.atan2(v.position_y, v.position_x)

            v.last_seen = time.time()
            v.msg_count += 1
            v.trail.append((v.position_x, v.position_y))

    # ── Public access (called from Qt main thread) ──

    def snapshot(self) -> Dict[int, VehicleState]:
        """Return a shallow copy of the vehicle dict (thread-safe)."""
        with self._lock:
            return dict(self._vehicles)

    # ── Lifecycle ──

    def start_spin(self):
        """Spin the ROS node in a daemon thread."""
        self._spin_thread = threading.Thread(
            target=rclpy.spin, args=(self._node,), daemon=True
        )
        self._spin_thread.start()

    def shutdown(self):
        self._node.destroy_node()