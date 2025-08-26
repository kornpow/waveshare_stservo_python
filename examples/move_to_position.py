#!/usr/bin/env python
#-*- coding:utf-8 -*-
#-Author:   waveshare
#-Website:  https://www.waveshare.com/
#-Update:   2024-05-20

import sys
import time
import argparse
from stservo.sdk import *

# Register Addresses
STS_GOAL_POSITION_L = 42
STS_TORQUE_ENABLE = 40

# Default settings
DEFAULT_BAUDRATE = 1000000

def move_servo(port, baudrate, servo_id, position):
    """
    Connects to a servo and moves it to a specified position using a direct write command.

    Args:
        port (str): The serial port name.
        baudrate (int): The communication baud rate.
        servo_id (int): The ID of the servo to control.
        position (int): The target position (0-4095).
    """
    portHandler = PortHandler(port)
    packetHandler = sts(portHandler)

    # Open port and set baudrate
    if not portHandler.openPort() or not portHandler.setBaudRate(baudrate):
        print(f"Error: Failed to connect to the servo at {port}")
        return

    print(f"Successfully connected to {port} at {baudrate} baud.")

    # Enable torque
    comm_result, error = packetHandler.write1ByteTxRx(servo_id, STS_TORQUE_ENABLE, 1)
    if comm_result != COMM_SUCCESS or error != 0:
        print("Error: Failed to enable torque.")
        portHandler.closePort()
        return

    print(f"Torque enabled for servo ID: {servo_id}")

    # Write the goal position directly to the register
    print(f"Moving servo {servo_id} to position {position}...")
    comm_result, error = packetHandler.write2ByteTxRx(servo_id, STS_GOAL_POSITION_L, position)
    if comm_result != COMM_SUCCESS or error != 0:
        print("Error: Failed to write position.")
    else:
        print("Position written successfully.")

    # Allow time for the move to complete
    time.sleep(1.5)

    # Disable torque
    packetHandler.write1ByteTxRx(servo_id, STS_TORQUE_ENABLE, 0)
    print("Torque disabled.")

    # Close the port
    portHandler.closePort()
    print("Port closed.")

def main():
    """
    Parses command-line arguments and initiates the servo movement.
    """
    parser = argparse.ArgumentParser(description="Move a single ST/SCS servo to a specific position.")
    parser.add_argument(
        "position",
        type=int,
        help="The target position for the servo (0-4095)."
    )
    parser.add_argument(
        "--port",
        type=str,
        default="/dev/tty.usbmodem5A680123831",
        help="The serial port for the servo controller."
    )
    parser.add_argument(
        "--servo-id",
        type=int,
        default=1,
        help="The ID of the servo to control."
    )
    parser.add_argument(
        "--baudrate",
        type=int,
        default=DEFAULT_BAUDRATE,
        help="The baud rate for serial communication."
    )

    args = parser.parse_args()

    if not (0 <= args.position <= 4095):
        print("Error: Position must be between 0 and 4095.")
        sys.exit(1)

    move_servo(
        port=args.port,
        baudrate=args.baudrate,
        servo_id=args.servo_id,
        position=args.position
    )

if __name__ == "__main__":
    main()
