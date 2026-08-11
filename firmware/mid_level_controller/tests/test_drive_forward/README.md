# Vehicle Drive Forward Test Script

## Overview

This script (`test_drive_forward.py`) sends DDS VehicleCommandDirect messages to control a vehicle through the mid-level controller (MLC). It can be used to test vehicle control commands and verify the communication pipeline.

## Features

- Send throttle and steering commands to a specific vehicle ID
- Configurable command duration and publishing rate
- Automatic stop command after test completion
- Support for both simulation mode and actual DDS communication
- Safe Ctrl+C handling with emergency stop

## Usage

### Basic Usage (Simulation Mode)

```bash
# Drive forward at 30% throttle for 5 seconds
python3 test_drive_forward.py --simulate --vehicle_id 1 --throttle 0.3

# Drive forward and turn left
python3 test_drive_forward.py --simulate --vehicle_id 1 --throttle 0.3 --steering 0.5

# Drive backward
python3 test_drive_forward.py --simulate --vehicle_id 1 --throttle -0.2
```

### Command Line Arguments

- `--vehicle_id ID`: Vehicle ID to control (1-255, default: 1)
- `--throttle VALUE`: Motor throttle in [-1, 1] (default: 0.3)
  - `1.0` = Max forward
  - `0.0` = Brake/stop
  - `-1.0` = Max reverse
- `--steering VALUE`: Steering servo in [-1, 1] (default: 0.0)
  - `1.0` = Max left
  - `0.0` = Center
  - `-1.0` = Max right
- `--duration SECONDS`: How long to send commands (default: 5.0)
- `--rate HZ`: Publishing rate in Hz (default: 50)
- `--dds_domain ID`: DDS domain ID (default: 0)
- `--simulate`: Force simulation mode (no actual DDS)

### View Help

```bash
python3 test_drive_forward.py --help
```

## Setting Up for Actual DDS Communication

To use this script with real DDS communication (not simulation mode), you need:

### 1. Install FastDDS Python Bindings

FastDDS Python bindings should already be installed if you have the FastDDS Python workspace set up:

```bash
# Source the FastDDS Python workspace
source ~/Documents/fastdds_python_ws/install/setup.bash
```

### 2. Generate Python Types from IDL

The script needs Python type modules generated from the IDL files:

```bash
cd /home/piracer/projects/cpm-lab/cpm_lib/dds_idl

# Generate Python bindings for required types
fastddsgen -python VehicleCommandDirect.idl
fastddsgen -python Header.idl
fastddsgen -python TimeStamp.idl

# Add the generated files to Python path
export PYTHONPATH=$PYTHONPATH:$(pwd)
```

### 3. Run with DDS

Once the above setup is complete, run without `--simulate`:

```bash
python3 test_drive_forward.py --vehicle_id 1 --throttle 0.3
```

## Safety Features

- Validates all input ranges before execution
- Sends stop command (throttle=0) on completion
- Sends stop command on Ctrl+C interrupt
- Provides clear feedback on simulation vs. real mode

## DDS Topic Information

The script publishes to the topic:
```
vehicle/{vehicle_id}/vehicleCommandDirect
```

Message type: `VehicleCommandDirect`

Message structure:
```
struct VehicleCommandDirect {
    uint8 vehicle_id;
    Header _header;           // Contains create_stamp and valid_after_stamp
    double motor_throttle;    // Range: [-1.0, 1.0]
    double steering_servo;    // Range: [-1.0, 1.0]
};
```

## Examples

### Test Forward Motion
```bash
python3 test_drive_forward.py --simulate --throttle 0.4 --duration 3
```

### Test Turning While Moving
```bash
# Left turn
python3 test_drive_forward.py --simulate --throttle 0.3 --steering 0.7

# Right turn
python3 test_drive_forward.py --simulate --throttle 0.3 --steering -0.7
```

### Test with Different Rates
```bash
# Fast updates (100 Hz)
python3 test_drive_forward.py --simulate --rate 100

# Slow updates (10 Hz)
python3 test_drive_forward.py --simulate --rate 10
```

### Control Multiple Vehicles (requires multiple terminals)
```bash
# Terminal 1
python3 test_drive_forward.py --vehicle_id 1 --throttle 0.3

# Terminal 2
python3 test_drive_forward.py --vehicle_id 2 --throttle 0.3
```

## Troubleshooting

### "FastDDS Python bindings not found"
- Make sure you've sourced the FastDDS Python workspace
- Install FastDDS Python bindings if not already installed

### "Could not import generated DDS types"
- Run fastddsgen to generate Python bindings from IDL files
- Add the IDL directory to PYTHONPATH

### Vehicle not responding
- Check that the vehicle MLC is running with the correct vehicle_id
- Verify DDS domain IDs match between script and MLC
- Check that the PCA9685 PWM hardware is properly initialized
- Monitor DDS traffic to ensure messages are being sent

### Messages sending but vehicle not moving
- Verify hardware connections (PCA9685, motors, servos)
- Check that throttle/steering values are in correct range
- Ensure the vehicle is not in a stop state from timeout

## Integration with MLC

This script interfaces with the mid-level controller (MLC) which:
1. Receives VehicleCommandDirect messages via DDS
2. Processes commands through the Controller module
3. Converts to motor and servo values
4. Sends PWM commands to PCA9685 for hardware control

The MLC expects commands at approximately 50 Hz to maintain active control. If no commands are received for a timeout period (default: 200ms), the vehicle will automatically stop for safety.
