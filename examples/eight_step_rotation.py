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

def move_servo(packet_handler, servo_id, position):
    """
    Moves a servo to a specified position using a direct write command.

    Args:
        packet_handler: The packet handler instance.
        servo_id (int): The ID of the servo to control.
        position (int): The target position (0-4095).
    """
    print(f"Moving servo {servo_id} to position {position}...")
    comm_result, error = packet_handler.write2ByteTxRx(servo_id, STS_GOAL_POSITION_L, position)
    if comm_result != COMM_SUCCESS or error != 0:
        print("Error: Failed to write position.")
    else:
        print("Position written successfully.")

def main():
    """
    Parses command-line arguments and cycles the servo through 8 positions.
    """
    parser = argparse.ArgumentParser(description="Cycle a servo through 8 positions (360 degrees).")
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

    portHandler = PortHandler(args.port)
    packetHandler = sts(portHandler)

    # Open port and set baudrate
    if not portHandler.openPort() or not portHandler.setBaudRate(args.baudrate):
        print(f"Error: Failed to connect to the servo at {args.port}")
        return

    print(f"Successfully connected to {args.port} at {args.baudrate} baud.")

    # Enable torque
    comm_result, error = packetHandler.write1ByteTxRx(args.servo_id, STS_TORQUE_ENABLE, 1)
    if comm_result != COMM_SUCCESS or error != 0:
        print("Error: Failed to enable torque.")
        portHandler.closePort()
        return

    print(f"Torque enabled for servo ID: {args.servo_id}")

    # Define the 8 positions for a 360-degree rotation (4096 / 8 = 512)
    positions = [0, 512, 1024, 1536, 2048, 2560, 3072, 3584]

    try:
        print("\nStarting 8-step rotation cycle. Press Ctrl+C to exit.")
        while True:
            for i, pos in enumerate(positions):
                print(f"\n--- Step {i+1}/8 ---")
                move_servo(packetHandler, args.servo_id, pos)
                time.sleep(1) # Wait for 1 second

    except KeyboardInterrupt:
        print("\nCycle interrupted by user.")

    finally:
        # Disable torque and close the port
        print("Disabling torque and closing port...")
        packetHandler.write1ByteTxRx(args.servo_id, STS_TORQUE_ENABLE, 0)
        portHandler.closePort()
        print("Port closed.")

if __name__ == "__main__":
    main()
