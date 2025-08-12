# sparton_ahrs8_driver

## 🟣 Branch for macOS and Mamba

This branch (`b166er`) is specifically adapted for use on **macOS** and with the **Mamba** environment manager. If you are using macOS, follow the instructions below to set up your environment and run the driver.

For **detailed instructions and troubleshooting**, see [`macOS_Mamba_SETUP.md`](macOS_Mamba_SETUP.md).

### 💻 macOS USB Serial Device Orientation

On macOS, USB serial devices typically appear as `/dev/tty.usbserial-*` or `/dev/tty.usbmodem-*`.

To find your device:
```bash
ls /dev/tty.usb*
# Example output: /dev/tty.usbserial-1420
```

Update the `port` parameter in your launch file or configuration to match your device, e.g.:
```xml
<param name="port" value="/dev/tty.usbserial-1420" />
```

If you have connection issues, ensure you have the correct drivers installed for your USB-to-serial adapter and check permissions as described in the setup file.

#### 📝 Example: Launch File Configuration (macOS)

Suppose your device is `/dev/tty.usbserial-1420`. Edit your launch file (`launch/ahrs-8.launch`) as follows:

```xml
<launch>
  <node pkg="sparton_ahrs8_driver" type="ahrs8_nmea.py" name="ahrs8_nmea" output="screen">
    <param name="port" value="/dev/tty.usbserial-1420" />
    <param name="baud" value="115200" />
    <param name="frame_id" value="ahrs8_imu" />
  </node>
</launch>
```

#### 📝 Example: Python Script Usage (macOS)

You can also run the script directly, specifying the port:

```bash
mamba activate sparton
python scripts/ahrs8_nmea.py --port /dev/tty.usbserial-1420 --baud 115200 --frame_id ahrs8_imu
```

### 🚀 Quick Start (macOS + Mamba)

1. **Clone this branch:**
  ```bash
  git clone -b b166er https://github.com/mhar-vell/sparton_ahrs8_driver.git
  cd sparton_ahrs8_driver
  ```

2. **Install [Mamba](https://github.com/mamba-org/mamba):**
  ```bash
  brew install mamba
  # or follow instructions at https://github.com/mamba-org/mamba
  ```

3. **Create and activate environment:**
  ```bash
  mamba create -n sparton python=3.10
  mamba activate sparton
  mamba install ros-noetic-desktop-full
  # Install any other dependencies as needed
  ```

4. **Build and run as usual (see below for details).**


## 🟣 Overview

This is a ROS package for interfacing with the [Sparton AHRS-8](https://www.spartonnavex.com/product/ahrs-8/) hardware. In particular, it communicates with the sensor using NMEA protocol and publishes the IMU data as ROS sensor messages.

The `sparton_ahrs8_driver` package has been tested under [ROS](http://www.ros.org) Kinetic and Ubuntu 16.04 LTS. The source code is released under a [MIT License](LICENSE.md).

> **Note:** This branch is updated for compatibility with macOS and mamba. For Linux/Ubuntu, use the `master` branch.

## 🟣 Usage

1. Clone the repository to your catkin workspace:
```bash
# For macOS and mamba, see instructions above.
cd ~/catkin_ws/src
git clone https://github.com/mhar-vell/sparton_ahrs8_driver.git -b b166er
```
2. Build the package:
```bash
cd ~/catkin_ws
catkin build sparton_ahrs8_driver
```
3. Check the serial port to which the sensor is connected at and change the device path in the [launch file](launch/ahrs-8.launch)
```bash
# to verify if device is at /dev/ttyUSB0, run:
udevadm info -a -p  $(udevadm info -q path -n /dev/ttyUSB0)
```
4. Ensure that python cript has executable permission:
```bash
chmod +x sparton_ahrs8_driver/scripts/ahrs8_nmea.py
```
5. Run the launch file:
```bash
roslaunch sparton_ahrs8_driver ahrs-8.launch
```

## 🟣 Node

### 📡 ahrs8_nmea.py

The node communicate with the sensor using the NMEA protocol and publishes IMU data.

#### ⚙️ Parameters
* **`~frame_id`** (string, default: `ahrs8_imu`)
  Frame ID for this plugin
* **`~port`** (string, default: `/dev/ttyUSB0`)
  Port at which sensor is connected
* **`~baud`** (double, default: `115200`)
  Baud rate for communication with the sensor

#### 📤 Published Topics

* **`~imu/data`** ([sensor_msgs/Imu])
  IMU orientation data, orientation in the `ahrs8_imu` frame

[sensor_msgs/Imu]: http://docs.ros.org/api/sensor_msgs/html/msg/Imu.html
