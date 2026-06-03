#!/usr/bin/env python3
"""Entry point for the IPS Vehicle Observation Visualizer."""

import sys

import rclpy
from PyQt5.QtWidgets import QApplication

from .ros_bridge import ROSBridge
from .main_window import MainWindow


def main():
    rclpy.init()

    bridge = ROSBridge(num_vehicles=20)
    bridge.start_spin()

    app = QApplication(sys.argv)
    window = MainWindow(bridge)
    window.show()

    exit_code = app.exec_()

    bridge.shutdown()
    rclpy.shutdown()
    sys.exit(exit_code)


if __name__ == "__main__":
    main()