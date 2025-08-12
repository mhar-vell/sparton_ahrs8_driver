# macOS + Mamba Setup Details for b166er Branch

This section provides further details for users on macOS using the `b166er` branch and mamba for environment management.

## Environment Setup

### 1. Install Homebrew (if not already installed)
```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
```

### 2. Install Mamba
```bash
brew install mamba
```

### 3. Create and Activate Environment
```bash
mamba create -n sparton python=3.10
mamba activate sparton
```

### 4. Install ROS Noetic (macOS)
ROS Noetic is not officially supported on macOS, but you can use [ros-noetic-desktop-full](https://github.com/marcoreis/ros-noetic-macos) or [homebrew-ros](https://github.com/marcoreis/homebrew-ros) for experimental support. Follow the instructions in those repositories for installation.

### 5. Install Python Dependencies
```bash
mamba install numpy pyserial catkin_pkg
```

## Device Setup (macOS)

- Check your serial device using:
  ```bash
  ls /dev/tty.*
  # Example: /dev/tty.usbserial-1420
  ```
- Update the device path in your launch file accordingly.

## Running the Driver

- Make sure your Python script is executable:
  ```bash
  chmod +x scripts/ahrs8_nmea.py
  ```
- Launch the node:
  ```bash
  roslaunch sparton_ahrs8_driver ahrs-8.launch
  ```

## Troubleshooting

- If you encounter permission issues with the serial port, add your user to the `tty` and `uucp` groups:
  ```bash
  sudo dseditgroup -o edit -a $(whoami) -t user tty
  sudo dseditgroup -o edit -a $(whoami) -t user uucp
  ```
- For mamba/conda environment issues, ensure you are using the correct Python version and all dependencies are installed.

## References
- [Mamba Documentation](https://mamba.readthedocs.io/en/latest/)
- [ROS Noetic on macOS](https://github.com/marcoreis/ros-noetic-macos)
- [Homebrew ROS](https://github.com/marcoreis/homebrew-ros)

---

For further help, open an issue on this branch or contact the maintainer.
