#!/usr/bin/env python3
"""
Test script to send DDS VehicleCommandDirect messages to control a vehicle.

Sends 5 drive forward commands to the specified vehicle.

Requirements:
    - FastDDS Python bindings installed
    - Generated Python types from IDL files in PYTHONPATH
    
Usage:
    python3 test_drive_forward.py --vehicle_id 1 [--dds_domain 0]
"""

import argparse
import time
import sys

from fastdds import *


class VehicleCommandDirectPublisher:
    """Publisher for VehicleCommandDirect messages."""
    
    def __init__(self, vehicle_id, dds_domain=0):
        """
        Initialize the DDS publisher.
        
        Args:
            vehicle_id: ID of the vehicle to control
            dds_domain: DDS domain ID (default: 0)
        """
        # Import generated DDS types
        try:
            from VehicleCommandDirect import VehicleCommandDirect, VehicleCommandDirectPubSubType
            self.VehicleCommandDirect = VehicleCommandDirect
            self.VehicleCommandDirectPubSubType = VehicleCommandDirectPubSubType
        except ImportError as e:
            print(f"Error: Could not import generated DDS types: {e}")
            print("\nPlease generate Python types from IDL files:")
            print("  cd ../cpm_lib/dds_idl")
            print("  fastddsgen -python VehicleCommandDirect.idl Header.idl TimeStamp.idl")
            print("  export PYTHONPATH=$PYTHONPATH:$(pwd)")
            raise
        
        self.vehicle_id = vehicle_id
        self.dds_domain = dds_domain
        self.topic_name = f"vehicle/{vehicle_id}/vehicleCommandDirect"
        
        # Create DDS participant
        factory = DomainParticipantFactory.get_instance()
        participant_qos = DomainParticipantQos()
        factory.get_default_participant_qos(participant_qos)
        
        self.participant = factory.create_participant(
            self.dds_domain, 
            participant_qos,
            None,
            StatusMask.all()
        )
        
        if self.participant is None:
            raise RuntimeError("Failed to create DDS participant")
        
        # Register type
        type_support_obj = self.VehicleCommandDirectPubSubType()
        self.type_support = TypeSupport(type_support_obj)
        self.type_name = type_support_obj.get_name()
        self.participant.register_type(self.type_support, self.type_name)
        
        # Create topic
        topic_qos = TopicQos()
        self.participant.get_default_topic_qos(topic_qos)
        self.topic = self.participant.create_topic(
            self.topic_name,
            self.type_name,
            topic_qos
        )
        
        if self.topic is None:
            raise RuntimeError("Failed to create topic")
        
        # Create publisher
        publisher_qos = PublisherQos()
        self.participant.get_default_publisher_qos(publisher_qos)
        self.publisher = self.participant.create_publisher(publisher_qos, None, StatusMask.all())
        
        if self.publisher is None:
            raise RuntimeError("Failed to create publisher")
        
        # Create data writer
        writer_qos = DataWriterQos()
        self.publisher.get_default_datawriter_qos(writer_qos)
        self.writer = self.publisher.create_datawriter(self.topic, writer_qos, None, StatusMask.all())
        
        if self.writer is None:
            raise RuntimeError("Failed to create data writer")
        
        print(f"DDS Publisher created for topic: {self.topic_name}")
    
    def publish_command(self, motor_throttle, steering_servo):
        """
        Publish a VehicleCommandDirect message.
        
        Args:
            motor_throttle: Throttle value in [-1, 1]
            steering_servo: Steering value in [-1, 1]
        """
        current_time_ns = int(time.time() * 1e9)
        
        message = self.VehicleCommandDirect()
        message.vehicle_id(self.vehicle_id)
        message.header().create_stamp().nanoseconds(current_time_ns)
        message.header().valid_after_stamp().nanoseconds(current_time_ns)
        message.motor_throttle(motor_throttle)
        message.steering_servo(steering_servo)
        
        self.writer.write(message)
        
        print(f"Sent command: throttle={motor_throttle:+.2f}, steering={steering_servo:+.2f}")
    
    def cleanup(self):
        """Clean up DDS resources."""
        if hasattr(self, 'participant') and self.participant is not None:
            factory = DomainParticipantFactory.get_instance()
            self.participant.delete_contained_entities()
            factory.delete_participant(self.participant)


def main():
    """Send 5 drive forward commands to the vehicle."""
    parser = argparse.ArgumentParser(
        description='Send 5 VehicleCommandDirect messages to drive a vehicle forward.'
    )
    parser.add_argument('--vehicle_id', type=int, required=True,
                       help='Vehicle ID to control (1-255)')
    parser.add_argument('--dds_domain', type=int, default=0,
                       help='DDS domain ID (default: 0)')
    
    args = parser.parse_args()
    
    # Validate vehicle ID
    if args.vehicle_id < 1 or args.vehicle_id > 255:
        print("Error: vehicle_id must be in range [1, 255]")
        sys.exit(1)
    
    print("=" * 60)
    print("Vehicle Drive Forward Test")
    print("=" * 60)
    print(f"Vehicle ID:   {args.vehicle_id}")
    print(f"DDS Domain:   {args.dds_domain}")
    print(f"Commands:     5 forward drive commands")
    print("=" * 60)
    print()
    
    try:
        # Create publisher
        publisher = VehicleCommandDirectPublisher(args.vehicle_id, args.dds_domain)
        
        # Give DDS time to match with subscribers
        time.sleep(0.5)
        
        for _ in range(10):
            # Send 5 drive forward commands
            # throttle = 0.3 (30% forward), steering = 0.0 (center)
            for i in range(25):
                print(f"[{i+1}/5] ", end="")
                publisher.publish_command(motor_throttle=0.30, steering_servo=1)
                time.sleep(0.1)  # 100ms between commands
            # for i in range(25):
            #    publisher.publish_command(motor_throttle=0.30, steering_servo=-1)
            #    time.sleep(0.1)

        # try steering left and right
        # print("\nTesting steering left and right:")
        # publisher.publish_command(motor_throttle=0.25, steering_servo=-1)  # steer left
        # time.sleep(0.1)
        # publisher.publish_command(motor_throttle=0.15, steering_servo=1)   # steer right
        # time.sleep(0.1)
        # publisher.publish_command(motor_throttle=0.15, steering_servo=0)   # back to center
        
        
        
        print()
        print("All commands sent successfully!")
        
        # Cleanup
        publisher.cleanup()
        
    except KeyboardInterrupt:
        print("\nInterrupted by user!")
        try:
            publisher.cleanup()
        except:
            pass
        sys.exit(0)
    
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
