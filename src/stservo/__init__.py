"""
STServo Python Library

A comprehensive Python library for controlling Waveshare STServos.

This package provides:
- Complete SDK for STServo communication
- High-level control functions for easy servo manipulation
- GUI application for servo control
- Utilities for discovery and configuration
"""

__version__ = "1.0.0"
__author__ = "iltlo"
__email__ = "iltlo@connect.hku.hk"

# Import main SDK components
from .utils import check_port


try:
    from .sdk import (
        PortHandler,
        sts,
        COMM_SUCCESS,
        STS_TORQUE_ENABLE,
        STS_ID,
        STS_PRESENT_POSITION_L,
        STS_PRESENT_SPEED_L,
        STS_PRESENT_LOAD_L,
        STS_MODE,
    )
    
    # Import control functions
    from .control import (
        move_servo,
        set_torque,
        check_position,
        wait_for_move_completion,
        DEFAULT_BAUDRATE,
        STS_MOVING_SPEED,
        STS_ACC,
    )
    
    # Import utilities (optional)
    try:
        from .utils import find_servo
        __all__ = [
            # SDK components
            "PortHandler",
            "sts", 
            "COMM_SUCCESS",
            "STS_TORQUE_ENABLE",
            "STS_ID",
            "STS_PRESENT_POSITION_L",
            "STS_PRESENT_SPEED_L",
            "STS_PRESENT_LOAD_L",
            "STS_MODE",
            # Control functions
            "move_servo",
            "set_torque",
            "check_position",
            "wait_for_move_completion",
            "DEFAULT_BAUDRATE",
            "STS_MOVING_SPEED",
            "STS_ACC",
            # Utilities
            "find_servo",
            "check_port",
        ]
    except ImportError:
        __all__ = [
            # SDK components
            "PortHandler",
            "sts", 
            "COMM_SUCCESS",
            "STS_TORQUE_ENABLE", 
            "STS_ID",
            "STS_PRESENT_POSITION_L",
            "STS_PRESENT_SPEED_L",
            "STS_PRESENT_LOAD_L", 
            "STS_MODE",
            # Control functions
            "move_servo",
            "set_torque",
            "check_position",
            "wait_for_move_completion",
            "DEFAULT_BAUDRATE",
            "STS_MOVING_SPEED",
            "STS_ACC",
            # Utilities
            "check_port",
        ]
        
except ImportError as e:
    print(f"Warning: Could not import SDK components: {e}")
    __all__ = []
