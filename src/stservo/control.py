"""
Control functions for STServo motors.

This module provides high-level control functions for STServo motors,
including position control, torque management, and movement monitoring.
"""

import time
from typing import Any, Tuple, Optional

from .sdk import PortHandler, sts

# Register Addresses
STS_TORQUE_ENABLE = 40
STS_PRESENT_POSITION_L = 56

# Default settings
DEFAULT_BAUDRATE = 1000000
STS_MOVING_SPEED = 2400
STS_ACC = 50

# Communication results
COMM_SUCCESS = 0


def set_torque(packetHandler: Any, servo_id: int, enable: bool) -> None:
    """
    Enables or disables the servo's torque.
    
    Args:
        packetHandler: The packet handler instance for communication
        servo_id: The ID of the servo to control
        enable: True to enable torque, False to disable
        
    Raises:
        RuntimeError: If the command fails
    """
    status_str = "enable" if enable else "disable"
    comm_result, error = packetHandler.write1ByteTxRx(
        servo_id, STS_TORQUE_ENABLE, 1 if enable else 0
    )
    if comm_result != COMM_SUCCESS or error != 0:
        raise RuntimeError(
            f"Failed to {status_str} torque for servo ID {servo_id}"
        )


def check_position(packetHandler: Any, servo_id: int) -> Tuple[int, bool]:
    """
    Reads and returns the current position of the servo.
    
    Args:
        packetHandler: The packet handler instance for communication
        servo_id: The ID of the servo to check
        
    Returns:
        A tuple of (position, success) where position is the current position
        and success is True if the read was successful
    """
    position, comm_result, error = packetHandler.read2ByteTxRx(
        servo_id, STS_PRESENT_POSITION_L
    )
    if comm_result != COMM_SUCCESS or error != 0:
        return -1, False
    return position, True


def wait_for_move_completion(
    packetHandler: Any,
    servo_id: int,
    timeout: int = 10,
    verbose: bool = True
) -> bool:
    """
    Waits for the servo to stop moving by polling its position.
    
    The move is considered complete when the position is stable for 0.25 seconds.
    
    Args:
        packetHandler: The packet handler instance for communication
        servo_id: The ID of the servo to monitor
        timeout: Maximum time to wait in seconds
        verbose: Whether to print status messages
        
    Returns:
        True if the move completes, False on timeout
    """
    # Initial delay to allow the move to start
    time.sleep(0.5)

    start_time = time.time()
    last_position, success = check_position(packetHandler, servo_id)
    if not success:
        if verbose:
            print("Error: Could not read initial position to check for move completion.")
        return False
    
    if verbose:
        print(f"Current position: {last_position}")
    time_at_last_change = time.time()

    while time.time() - start_time < timeout:
        current_position, success = check_position(packetHandler, servo_id)
        if not success:
            # On a read error, just continue and try again
            time.sleep(0.05)
            continue

        if current_position != last_position:
            last_position = current_position
            if verbose:
                print(f"Current position: {current_position}")
            time_at_last_change = time.time()
        
        # If position has been stable for 0.25 seconds, the move is complete
        if time.time() - time_at_last_change > 0.25:
            if verbose:
                print(f"Servo has stopped at position: {current_position}")
            return True

        time.sleep(0.05)  # Poll every 50ms

    if verbose:
        print("Warning: Timeout occurred while waiting for the servo to stop.")
    return False


def move_servo(
    port: str,
    servo_id: int,
    position: int,
    baudrate: int = DEFAULT_BAUDRATE,
    speed: int = STS_MOVING_SPEED,
    acceleration: int = STS_ACC,
    timeout: int = 10,
    verbose: bool = True
) -> bool:
    """
    Connects to a servo and moves it to a specified position.
    
    Args:
        port: The serial port path (e.g., '/dev/ttyUSB0' or 'COM3')
        servo_id: The ID of the servo to control
        position: Target position (0-4095)
        baudrate: Serial communication baud rate
        speed: Moving speed of the servo
        acceleration: Acceleration of the servo
        timeout: Maximum time to wait for move completion in seconds
        verbose: Whether to print status messages
        
    Returns:
        True if the move was successful, False otherwise
        
    Raises:
        ValueError: If position is out of range (0-4095)
    """
    if not (0 <= position <= 4095):
        raise ValueError("Position must be between 0 and 4095")
    
    portHandler = PortHandler(port)
    packetHandler = sts(portHandler)

    if not portHandler.openPort() or not portHandler.setBaudRate(baudrate):
        if verbose:
            print(f"Error: Failed to connect to the servo at {port}")
        return False

    if verbose:
        print(f"Successfully connected to {port} at {baudrate} baud.")

    try:
        set_torque(packetHandler, servo_id, True)
        if verbose:
            print(f"Torque enabled for servo ID: {servo_id}")

        # Send the move command
        if verbose:
            print(f"Moving servo {servo_id} to position {position}...")
        comm_result, error = packetHandler.WritePosEx(
            servo_id, position, speed, acceleration
        )
        if comm_result != COMM_SUCCESS or error != 0:
            if verbose:
                print("Error: Failed to write position.")
            return False
        else:
            if verbose:
                print("Position written successfully.")
            # Wait for the move to finish
            success = wait_for_move_completion(
                packetHandler, servo_id, timeout=timeout, verbose=verbose
            )
            return success

    except RuntimeError as e:
        if verbose:
            print(f"Error: {e}")
        return False
    finally:
        # Always try to disable torque and close the port
        try:
            set_torque(packetHandler, servo_id, False)
            if verbose:
                print(f"Torque disabled for servo ID: {servo_id}")
        except RuntimeError as e:
            if verbose:
                print(f"Warning: {e}")
        portHandler.closePort()
        if verbose:
            print("Port closed.")

