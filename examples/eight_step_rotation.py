#!/usr/bin/env python
#-*- coding:utf-8 -*-
#-Author:   waveshare
#-Website:  https://www.waveshare.com/
#-Update:   2024-05-20

import sys
import time
import argparse
import subprocess
import os
from datetime import datetime
from stservo.sdk import *

# Register Addresses
STS_GOAL_POSITION_L = 42
STS_TORQUE_ENABLE = 40

# Default settings
DEFAULT_BAUDRATE = 1000000
DEFAULT_SERVO_ID = 1

def move_servo(port, baudrate, servo_id, position):
    """
    Connects to a servo and moves it to a specified position using a direct write command.

    Args:
        port (str): The serial port name.
        baudrate (int): The communication baud rate.
        servo_id (int): The ID of the servo to control.
        position (int): The target position (0-4095).
    
    Returns:
        bool: True if successful, False otherwise.
    """
    portHandler = PortHandler(port)
    packetHandler = sts(portHandler)

    # Open port and set baudrate
    if not portHandler.openPort() or not portHandler.setBaudRate(baudrate):
        print(f"Error: Failed to connect to the servo at {port}")
        return False

    print(f"Successfully connected to {port} at {baudrate} baud.")

    # Enable torque
    comm_result, error = packetHandler.write1ByteTxRx(servo_id, STS_TORQUE_ENABLE, 1)
    if comm_result != COMM_SUCCESS or error != 0:
        print("Error: Failed to enable torque.")
        portHandler.closePort()
        return False

    print(f"Torque enabled for servo ID: {servo_id}")

    # Write the goal position directly to the register
    print(f"Moving servo {servo_id} to position {position}...")
    comm_result, error = packetHandler.write2ByteTxRx(servo_id, STS_GOAL_POSITION_L, position)
    if comm_result != COMM_SUCCESS or error != 0:
        print("Error: Failed to write position.")
        portHandler.closePort()
        return False
    else:
        print("Position written successfully.")

    # Allow time for the move to complete
    time.sleep(2)

    # Disable torque
    packetHandler.write1ByteTxRx(servo_id, STS_TORQUE_ENABLE, 0)
    print("Torque disabled.")

    # Close the port
    portHandler.closePort()
    print("Port closed.")
    
    return True

def take_photo(output_dir, position_index):
    """
    Takes a photo using rpicam-still command.
    
    Args:
        output_dir (str): Directory to save the photo.
        position_index (int): Index of the current position (0-7).
    
    Returns:
        bool: True if successful, False otherwise.
    """
    # Ensure output directory exists
    try:
        os.makedirs(output_dir, exist_ok=True)
    except Exception as e:
        print(f"Error creating output directory {output_dir}: {e}")
        return False
    
    filename = f"photo_{position_index:02d}.png"
    filepath = os.path.abspath(os.path.join(output_dir, filename))
    
    print(f"Taking photo: {filename}")
    print(f"Full path: {filepath}")
    
    try:
        # Run the rpicam-still command
        cmd = [
            "rpicam-still",
            "--width", "1280",
            "--height", "720", 
            "--immediate",
            "--output", filepath,
            "--datetime"
        ]
        
        print(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        
        if result.returncode == 0:
            # Check if file was actually created
            if os.path.exists(filepath):
                print(f"Photo saved successfully: {filepath}")
                return True
            else:
                print(f"Error: Photo file was not created at {filepath}")
                return False
        else:
            print(f"Error taking photo (return code {result.returncode}):")
            if result.stderr:
                print(f"STDERR: {result.stderr}")
            if result.stdout:
                print(f"STDOUT: {result.stdout}")
            return False
            
    except subprocess.TimeoutExpired:
        print("Error: Camera command timed out")
        return False
    except Exception as e:
        print(f"Error taking photo: {e}")
        return False

def eight_step_rotation_with_photos(port, baudrate, servo_id, output_dir, start_position=0, end_position=4095):
    """
    Moves servo through 8 equal distant positions and takes a photo at each position.
    
    Args:
        port (str): The serial port name.
        baudrate (int): The communication baud rate.
        servo_id (int): The ID of the servo to control.
        output_dir (str): Directory to save photos.
        start_position (int): Starting position (default: 0).
        end_position (int): Ending position (default: 4095).
    """
    # Create output directory if it doesn't exist
    try:
        output_dir = os.path.abspath(output_dir)
        os.makedirs(output_dir, exist_ok=True)
        print(f"Output directory created/verified: {output_dir}")
    except Exception as e:
        print(f"Error creating output directory {output_dir}: {e}")
        return
    
    # Calculate 8 equal distant positions
    step = (end_position - start_position) / 7  # 7 steps to get 8 positions
    positions = [int(start_position + i * step) for i in range(8)]
    
    print(f"Starting 8-step rotation with photos")
    print(f"Positions: {positions}")
    print(f"Output directory: {output_dir}")
    print("-" * 50)
    
    successful_photos = 0
    
    for i, position in enumerate(positions):
        print(f"\nStep {i+1}/8: Moving to position {position}")
        
        # Move servo to position
        if move_servo(port, baudrate, servo_id, position):
            # Wait a moment for servo to settle
            time.sleep(1)
            
            # Take photo
            if take_photo(output_dir, i):
                successful_photos += 1
            else:
                print(f"Failed to take photo at position {position}")
        else:
            print(f"Failed to move servo to position {position}")
    
    print("-" * 50)
    print(f"Rotation complete! {successful_photos}/8 photos taken successfully.")
    print(f"Photos saved in: {output_dir}")

def main():
    """
    Parses command-line arguments and initiates the 8-step rotation with photos.
    """
    parser = argparse.ArgumentParser(description="Move servo through 8 positions and take photos at each position.")
    parser.add_argument(
        "--port",
        type=str,
        default="/dev/tty.usbmodem5A680123831",
        help="The serial port for the servo controller."
    )
    parser.add_argument(
        "--servo-id",
        type=int,
        default=DEFAULT_SERVO_ID,
        help="The ID of the servo to control."
    )
    parser.add_argument(
        "--baudrate",
        type=int,
        default=DEFAULT_BAUDRATE,
        help="The baud rate for serial communication."
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="./photos",
        help="Directory to save the photos."
    )
    parser.add_argument(
        "--start-position",
        type=int,
        default=0,
        help="Starting position for rotation (0-4095)."
    )
    parser.add_argument(
        "--end-position",
        type=int,
        default=4095,
        help="Ending position for rotation (0-4095)."
    )

    args = parser.parse_args()

    # Validate positions
    if not (0 <= args.start_position <= 4095):
        print("Error: Start position must be between 0 and 4095.")
        sys.exit(1)
    
    if not (0 <= args.end_position <= 4095):
        print("Error: End position must be between 0 and 4095.")
        sys.exit(1)
    
    if args.start_position >= args.end_position:
        print("Error: Start position must be less than end position.")
        sys.exit(1)

    eight_step_rotation_with_photos(
        port=args.port,
        baudrate=args.baudrate,
        servo_id=args.servo_id,
        output_dir=args.output_dir,
        start_position=args.start_position,
        end_position=args.end_position
    )

if __name__ == "__main__":
    main()