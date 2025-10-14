#!/usr/bin/env python
"""
Example: Move a servo to a specific position using the high-level control API.

This example demonstrates how to use the move_servo() function from the stservo
package to easily control servo position.
"""

import sys
import os
import argparse

# Import the high-level control function
from stservo import move_servo, DEFAULT_BAUDRATE, STS_MOVING_SPEED, STS_ACC

# Import config
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', 'config')))
try:
    from device_config import load_device_port
except ImportError:
    def load_device_port():
        return "/dev/ttyACM0"


def main() -> None:
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
        default=load_device_port(),
        help="The serial port for the servo controller (e.g., /dev/ttyUSB0 or COM3)."
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
    parser.add_argument(
        "--timeout",
        type=int,
        default=10,
        help="The timeout in seconds to wait for the move to complete."
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="Suppress status messages."
    )

    args = parser.parse_args()

    if not (0 <= args.position <= 4095):
        print("Error: Position must be between 0 and 4095.")
        sys.exit(1)

    # Use the high-level move_servo function
    success = move_servo(
        port=args.port,
        servo_id=args.servo_id,
        position=args.position,
        baudrate=args.baudrate,
        speed=args.speed,
        acceleration=args.acceleration,
        timeout=args.timeout,
        verbose=not args.quiet
    )

    if not success:
        print("Error: Failed to move servo.")
        sys.exit(1)


if __name__ == "__main__":
    main()
