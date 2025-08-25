#!/usr/bin/env python
#-*- coding:utf-8 -*-
#-Author:   waveshare
#-Website:  https://www.waveshare.com/
#-Update:   2021-02-01

import sys
import time
from stservo.sdk import *

#
# Please modify the corresponding port name and baud rate according to the actual situation
#
DEVICENAME = "/dev/tty.usbmodem5A680123831"
BAUDRATE = 1000000

STS_ID = 1

# Protocol version
PROTOCOL_VERSION = 2.0

# Default setting
STS_MOVING_SPEED = 2400  # Starting speed
STS_ACC = 50           # Acceleration
STS_GOAL_POSITION = 0  # Goal position

# Other settings
COMM_SUCCESS = 0
COMM_TX_FAIL = -1001

def main():
    """
    Moves a servo to a specified position using the STServo SDK.
    """
    portHandler = PortHandler(DEVICENAME)
    packetHandler = sts(portHandler)

    # Open port
    if not portHandler.openPort():
        print("Failed to open the port")
        return

    # Set baudrate
    if not portHandler.setBaudRate(BAUDRATE):
        print("Failed to change the baudrate")
        return

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

    # Set goal position
    goal_position = int(input("Enter goal position (0-4095): "))
    if not (0 <= goal_position <= 4095):
        print("Invalid position. Must be between 0 and 4095.")
        portHandler.closePort()
        return

    # Move servo to goal position
    print(f"Moving servo with ID {STS_ID} to position {goal_position}...")
    dxl_comm_result, dxl_error = packetHandler.WritePosEx(STS_ID, goal_position, STS_MOVING_SPEED, STS_ACC)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Move failed: {packetHandler.getTxRxResult(dxl_comm_result)}")
    elif dxl_error != 0:
        print(f"Move error: {packetHandler.getRxPacketError(dxl_error)}")
    else:
        print(f"Successfully moved servo to position {goal_position}")

    # Wait for movement to complete
    time.sleep(2)

    # Disable torque
    dxl_comm_result, dxl_error = packetHandler.write1ByteTxRx(STS_ID, STS_TORQUE_ENABLE, 0)
    if dxl_comm_result != COMM_SUCCESS:
        print(f"Torque disable failed: {packetHandler.getTxRxResult(dxl_comm_result)}")
    elif dxl_error != 0:
        print(f"Torque disable error: {packetHandler.getRxPacketError(dxl_error)}")

    # Close port
    portHandler.closePort()

if __name__ == "__main__":
    main()
