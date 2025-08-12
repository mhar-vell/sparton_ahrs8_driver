# Device Rules for Sparton AHRS8

## Linux (udev rules)
The `51-sparton-ahrs8.rules` file contains udev rules for Linux systems that automatically create symlinks for Sparton AHRS8 devices.

### Installation on Linux:
```bash
sudo cp 51-sparton-ahrs8.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules
sudo udevadm trigger
```

## macOS
macOS doesn't support udev rules. Instead, USB serial devices appear as `/dev/tty.usbserial-XXXXXXXX` where XXXXXXXX is the FTDI chip's serial number.

### Finding Your Device on macOS:
1. **Automatic detection**: Use the provided helper script:
   ```bash
   python find_sparton_device.py
   ```

2. **Manual method**: List all USB serial devices:
   ```bash
   ls /dev/tty.usbserial-*
   ```

3. **Detailed device info**:
   ```bash
   system_profiler SPUSBDataType | grep -A 20 -B 5 "FTDI"
   ```

### Known Sparton AHRS8 Serial Numbers:
- FTFUUTW1
- FTFUXGRZ  
- FTFUT9EB

### Current Configuration:
The launch file and Python script are already configured for macOS using:
- Default device: `/dev/tty.usbserial-FTFUT9EB`
- This can be overridden via ROS parameters

### Usage:
```bash
# Use default device
roslaunch sparton_ahrs8_driver ahrs-8.launch

# Specify custom device
roslaunch sparton_ahrs8_driver ahrs-8.launch port:=/dev/tty.usbserial-YOURSERIAL
```
