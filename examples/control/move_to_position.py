#!/usr/bin/env python
#-*- coding:utf-8 -*-
#-Author:   waveshare
#-Website:  https://www.waveshare.com/
#-Update:   2024-05-20

import sys
import time
import argparse
from stservo.sdk import *

# Default settings
DEFAULT_BAUDRATE = 1000000
STS_ID = 1
STS_MOVING_SPEED = 2400  # Default moving speed
STS_ACC = 50           # Default acceleration

# Communication results
COMM_SUCCESS = 0

def move_servo(port, baudrate, servo_id, position, speed, acceleration):
    """
    Connects to a servo and moves it to a specified position.

    Args:
        port (str): The serial port name.
        baudrate (int): The communication baud rate.
        servo_id (int): The ID of the servo to control.
        position (int): The target position (0-4095).
        speed (int): The speed of movement.
        acceleration (int): The acceleration of the movement.
    """
    portHandler = PortHandler(port)
    packetHandler = sts(portHandler)

    # Open port
    if not portHandler.openPort():
        print(f"Error: Failed to open the port {port}")
        return

    # Set baudrate
    if not portHandler.setBaudRate(baudrate):
        print(f"Error: Failed to change the baudrate to {baudrate}")
        portHandler.closePort()
        return

    print(f"Successfully connected to {port} at {baudrate} baud.")

    # Enable torque
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(STS_ID, STS_TORQUE_ENABLE, 1)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Torque enable failed: {packetHandler.getTxRxResult(dxl_comm_result)}")
        portHandler.closePort()
        return
    elif dxl_error != 0:
        print(f"Torque enable error: {packetHandler.getRxPacketError(dxl_error)}")
        portHandler.closePort()
        return

    print(f"Torque enabled for servo ID: {servo_id}")

    # Move servo to the goal position
    print(f"Moving servo {servo_id} to position {position}...")
    dxl_comm_result, dxl_error = packetHandler.WritePosEx(servo_id, position, speed, acceleration)
    if dxl_comm_result != COMM_SUCCESS or dxl_error != 0:
        print("Error: Failed to move servo.")
        if dxl_comm_result != COMM_SUCCESS:
            print(f"Communication Error: {packetHandler.getTxRxResult(dxl_comm_result)}")
        if dxl_error != 0:
            print(f"Packet Error: {packetHandler.getRxPacketError(dxl_error)}")
    else:
        print("Servo moved successfully.")

    # Wait for the move to complete
    time.sleep(1)

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
        default="/dev/ttyACM0",
        help="The serial port for the servo controller (e.g., /dev/ttyUSB0 or COM3)."
    )
    parser.add_argument(
        "--servo-id",
        type=int,
        default=STS_ID,
        help="The ID of the servo to control."
    )
    parser.add_argument(
        "--baudrate",
        type=int,
        default=DEFAULT_BAUDRATE,
        help="The baud rate for serial communication."
    )
    parser.add_argument(
        "--speed",
        type=int,
        default=STS_MOVING_SPEED,
        help="The moving speed of the servo."
    )
    parser.add_argument(
        "--acceleration",
        type=int,
        default=STS_ACC,
        help="The acceleration of the servo."
    )

    args = parser.parse_args()

    if not (0 <= args.position <= 4095):
        print("Error: Position must be between 0 and 4095.")
        sys.exit(1)

    move_servo(
        port=args.port,
        baudrate=args.baudrate,
        servo_id=args.servo_id,
        position=args.position,
        speed=args.speed,
        acceleration=args.acceleration
    )

if __name__ == "__main__":
    main()
