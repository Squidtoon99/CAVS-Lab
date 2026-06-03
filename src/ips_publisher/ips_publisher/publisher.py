import math
import sys
import time
from scipy.spatial.transform import Rotation

import rclpy
from rclpy.node import Node
from rclpy.qos import QoSProfile, ReliabilityPolicy
from ips_interfaces.msg import VehicleObservation

import cv2
from pupil_apriltags import Detector
from pypylon import pylon, genicam

class VehicleDetectionNode(Node):
    def __init__(self):
        super().__init__('vehicle_detection_node')

        # 1. Declare ROS 2 Parameters with defaults from your config
        self.declare_parameters(
            namespace='',
            parameters=[
                ('camera.exposure', 771.0),              # microseconds
                ('camera.gain', 5.0),                    # dB
                ('camera.black_level', 15.0),            # Offset
                ('camera.fps', 30.0),                    # Target framerate
                ('apriltag.threads', 8),                 # Detection threads
                ('apriltag.quad_decimate', 2.0),         # Image resolution down-scaling
                ('apriltag.quad_sigma', 0.0),            # Gaussian blur noise correction
                ('apriltag.refine_edges', 1),            # Snap quads to gradients
                ('apriltag.decode_sharpening', 0.2),     # Sharpening of decoded images
                ('apriltag.tag_size', 0.15),             # Tag size in meters
                ('apriltag.camera_coefficients',[1800.0, 1800.0, 1024.0, 1024.0]), # [fx, fy, cx, cy]
                ('system.debug', False),                 # Debug UI disabled by default
                ('system.number_vehicles', 20)           # Max vehicle ID to track
            ]
        )

        # 2. Fetch Parameters
        self.camera_params = self.get_parameter('apriltag.camera_coefficients').value
        self.tag_size = self.get_parameter('apriltag.tag_size').value
        self.debug_mode = self.get_parameter('system.debug').value
        self.number_vehicles = self.get_parameter('system.number_vehicles').value
        camera_fps = self.get_parameter('camera.fps').value

        # 3. Initialize AprilTag Detector
        self.detector = Detector(
            families='tag36h11',
            nthreads=self.get_parameter('apriltag.threads').value,
            quad_decimate=self.get_parameter('apriltag.quad_decimate').value,
            quad_sigma=self.get_parameter('apriltag.quad_sigma').value,
            refine_edges=self.get_parameter('apriltag.refine_edges').value,
            decode_sharpening=self.get_parameter('apriltag.decode_sharpening').value,
        )

        # 4. Initialize Camera & Format Converter
        self.camera = None
        self.converter = pylon.ImageFormatConverter()
        self.converter.OutputPixelFormat = pylon.PixelType_Mono8
        self.converter.OutputBitAlignment = pylon.OutputBitAlignment_MsbAligned
        self.initialise_camera()

        # 5. Setup ROS Publishers
        qos = QoSProfile(depth=10, reliability=ReliabilityPolicy.BEST_EFFORT)
        self.observation_publishers = {}

        for i in range(0, self.number_vehicles):
            topic_name = f'vehicle_{i}/vehicleObservation'
            self.observation_publishers[i] = self.create_publisher(VehicleObservation, topic_name, qos)

        # 6. Setup Debug Window & Timing
        if self.debug_mode:
            self.window_name = 'IPS AprilTag Debug'
            cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
            cv2.resizeWindow(self.window_name, 800, 800)

        self.fps_start = time.time()
        self.frames = 0
        self.fps = 0.0

        # 7. Start Timer Loop
        timer_period = 1.0 / camera_fps
        self.timer = self.create_timer(timer_period, self.timer_callback)
        self.get_logger().info("AprilTag Positioning Node Initialized Successfully.")

    def initialise_camera(self):
        try:
            tl_factory = pylon.TlFactory.GetInstance()
            self.camera = pylon.InstantCamera(tl_factory.CreateFirstDevice())
            self.camera.Open()

            self.get_logger().info(f"Opened camera: {self.camera.GetDeviceInfo().GetModelName()}")

            self.camera.ExposureAuto.Value = 'Off'
            self.camera.ExposureTime.Value = self.get_parameter('camera.exposure').value
            self.camera.GainAuto.Value = 'Off'
            self.camera.Gain.Value = self.get_parameter('camera.gain').value
            self.camera.BlackLevel.Value = self.get_parameter('camera.black_level').value

            self.camera.StartGrabbing(pylon.GrabStrategy_LatestImageOnly)

        except genicam.GenericException as e:
            self.get_logger().error(f"Error while opening camera: {e.GetDescription()}")
            sys.exit(1)

    def timer_callback(self):
        if self.camera is None or not self.camera.IsGrabbing():
            return

        try:
            grabResult = self.camera.RetrieveResult(10, pylon.TimeoutHandling_Return)
        except genicam.GenericException as e:
            self.get_logger().error(f"Camera Grab Exception: {e.GetDescription()}")
            return

        # Record the exact time the frame was grabbed for latency compensation
        frame_time = self.get_clock().now().to_msg()

        if not grabResult or not grabResult.GrabSucceeded():
            if grabResult:
                grabResult.Release()
            return

        # Convert Image
        image = self.converter.Convert(grabResult)
        gray_img = image.GetArray()
        
        # AprilTag Detection
        detected = self.detector.detect(
            gray_img, 
            estimate_tag_pose=True, 
            camera_params=self.camera_params, 
            tag_size=self.tag_size
        )

        # Process & Publish Detected Tags
        for tag in detected:
            vehicle_id = tag.tag_id
            
            if vehicle_id not in self.observation_publishers:
                continue
            
            # --- POPULATE THE VehicleObservation MESSAGE ---
            obs_msg = VehicleObservation()
            
            # 1. ID
            obs_msg.vehicle_id = vehicle_id
            
            # 2. Standard Header
            obs_msg.header.stamp = frame_time
            obs_msg.header.frame_id = "map"
            
            # 3. Valid After Stamp (Compensating for camera/processing latency)
            obs_msg.valid_after_stamp = frame_time
            
            # 4. Pose - Position (tag.pose_t is a 3x1 translation vector)
            obs_msg.pose.position.x = float(tag.pose_t[0][0])
            obs_msg.pose.position.y = float(tag.pose_t[1][0])
            obs_msg.pose.position.z = float(tag.pose_t[2][0])


            
            obs_msg.pose.orientation.x = math.atan2(float(tag.pose_t[1][0]), float(tag.pose_t[0][0]))
            obs_msg.pose.orientation.y = 0
            obs_msg.pose.orientation.z = 0
            obs_msg.pose.orientation.w = 0

            # Publish the fully populated message
            self.observation_publishers[vehicle_id].publish(obs_msg)

        # Debug Visualization
        if self.debug_mode:
            self.render_debug_view(gray_img, detected)

        # Release the buffer back to Pylon
        grabResult.Release()

    def render_debug_view(self, gray_img, detected):
        display_img = cv2.cvtColor(gray_img, cv2.COLOR_GRAY2BGR)
        
        # FPS Calculation
        self.frames += 1
        current_time = time.time()
        if current_time - self.fps_start > 1.0:
            self.fps = self.frames / (current_time - self.fps_start)
            self.frames = 0
            self.fps_start = current_time

        # Status Overlay
        info_color = (0, 255, 0) if len(detected) > 0 else (0, 0, 255)
        cv2.putText(display_img, f"FPS: {self.fps:.1f}", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, info_color, 2)
        cv2.putText(display_img, f"Tags: {len(detected)}", (20, 90), cv2.FONT_HERSHEY_SIMPLEX, 1, info_color, 2)
        
        for tag in detected:
            # Draw Tag Bounding Box
            for idx in range(len(tag.corners)):
                pt1 = tuple(tag.corners[idx - 1].astype(int))
                pt2 = tuple(tag.corners[idx].astype(int))
                cv2.line(display_img, pt1, pt2, (0, 255, 0), 2)
            
            # Draw Orientation Arrow
            center = tuple(tag.center.astype(int))
            top = tuple(((tag.corners[2] + tag.corners[3]) / 2).astype(int))
            cv2.arrowedLine(display_img, center, top, (0, 0, 255), 4, tipLength=0.3)

            # Draw Tag ID
            cv2.putText(display_img, str(tag.tag_id), (center[0]-10, center[1]+10), 
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)

        cv2.imshow(self.window_name, display_img)
        cv2.waitKey(1)

    def destroy_node(self):
        self.get_logger().info("Shutting down AprilTag node and releasing camera...")
        if self.camera is not None and self.camera.IsOpen():
            self.camera.StopGrabbing()
            self.camera.Close()
        if self.debug_mode:
            cv2.destroyAllWindows()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = VehicleDetectionNode()
    
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()