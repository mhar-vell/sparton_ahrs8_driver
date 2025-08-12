#!/usr/bin/env python

"""
Helper script to find Sparton AHRS8 device on macOS
This replaces the udev rules functionality for macOS
"""

import glob
import subprocess
import re
import sys

def find_sparton_device():
    """
    Find Sparton AHRS8 device by looking for FTDI devices with known serial numbers
    Returns the device path or None if not found
    """
    # Known Sparton AHRS8 serial numbers (from udev rules)
    known_serials = ['FTFUUTW1', 'FTFUXGRZ', 'FTFUT9EB']
    
    # Find all USB serial devices
    tty_devices = glob.glob('/dev/tty.usbserial-*')
    
    for device in tty_devices:
        # Extract serial number from device name
        serial_match = re.search(r'/dev/tty\.usbserial-(.+)', device)
        if serial_match:
            serial = serial_match.group(1)
            if serial in known_serials:
                return device
    
    # Alternative method: use system_profiler to get more detailed info
    try:
        result = subprocess.run(['system_profiler', 'SPUSBDataType'], 
                              capture_output=True, text=True, check=False)
        if result.returncode == 0:
            # Look for FTDI devices with vendor ID 0x0403 and product ID 0x6001
            lines = result.stdout.split('\n')
            current_device = None
            for line in lines:
                if 'TTL232R' in line or 'FT232' in line:
                    current_device = line.strip().rstrip(':')
                elif 'Serial Number:' in line and current_device:
                    serial_match = re.search(r'Serial Number:\s*(\w+)', line)
                    if serial_match:
                        serial = serial_match.group(1)
                        if serial in known_serials:
                            device_path = f'/dev/tty.usbserial-{serial}'
                            if device_path in tty_devices:
                                return device_path
    except subprocess.SubprocessError:
        pass
    
    return None

def main():
    """Main function to find and print device path"""
    device = find_sparton_device()
    if device:
        print(device)
        return 0
    else:
        print("Sparton AHRS8 device not found", file=sys.stderr)
        print("Available USB serial devices:", file=sys.stderr)
        for dev in glob.glob('/dev/tty.usbserial-*'):
            print(f"  {dev}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
