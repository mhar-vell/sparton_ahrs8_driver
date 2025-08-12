#!/usr/bin/env python3

import rospy
import serial
import math
import glob
import os
from geometry_msgs.msg import Quaternion, Twist, Vector3
from sensor_msgs.msg import Imu

import tf
from tf.transformations import euler_from_quaternion, quaternion_from_euler

def find_sparton_device():
    """
    Find Sparton AHRS8 device on macOS/Linux
    Returns the device path or None if not found
    """
    # Known Sparton AHRS8 serial numbers
    known_serials = ['FTFUUTW1', 'FTFUXGRZ', 'FTFUT9EB']
    
    # Check for macOS USB serial devices
    macos_devices = glob.glob('/dev/tty.usbserial-*')
    for device in macos_devices:
        # Extract serial number from device name
        if any(serial in device for serial in known_serials):
            return device
    
    # Check for Linux USB devices  
    linux_devices = glob.glob('/dev/ttyUSB*')
    if linux_devices:
        # On Linux, we'd need to check udev info, but for now return first device
        # This could be enhanced to check actual serial numbers
        return linux_devices[0]
    
    return None

def verify_checksum(response):
    message_and_checksum = response.strip(b"$").split(b"*")
    if len(message_and_checksum) != 2:
        return False
    message, checksum = message_and_checksum
    checksum = checksum.strip()
    calculated_checksum = 0
    for character in message:
        calculated_checksum ^= character
    hexstring = '{:02X}'.format(calculated_checksum)
    return checksum.upper() == hexstring.encode('utf-8')

def populate_G(string, message):
    split_string = string.decode('utf-8').split(",")
    Gx_float = millidegrees_to_radians(float(split_string[1].split("=")[1]))
    Gy_float = millidegrees_to_radians(float(split_string[2].split("=")[1]))
    Gz_float = millidegrees_to_radians(float(split_string[3].split("*")[0].split("=")[1]))
    message.angular_velocity = Vector3(Gx_float, -Gy_float, -Gz_float)

def populate_QUAT(string, message):
    split_string = string.decode('utf-8').split(",")
    w_float = float(split_string[1].split("=")[1])
    x_float = float(split_string[2].split("=")[1])
    y_float = float(split_string[3].split("=")[1])
    z_float = float(split_string[4].split("*")[0].split("=")[1])
    euler = euler_from_quaternion([y_float, x_float, -z_float, w_float])
    quat = quaternion_from_euler(euler[0], euler[1], euler[2] + math.pi/2)
    message.orientation = Quaternion(quat[0], quat[1], quat[2], quat[3])

def populate_A(string, message):
    split_string = string.decode('utf-8').split(",")
    Ax_float = millig_to_meter(float(split_string[1].split("=")[1]))
    Ay_float = millig_to_meter(float(split_string[2].split("=")[1]))
    Az_float = millig_to_meter(float(split_string[3].split("*")[0].split("=")[1]))
    message.linear_acceleration = Vector3(-Ax_float, Ay_float, Az_float)

#def euler():
#    pub = rospy.Publisher('imu/euler', Vector3, queue_size=10)
#    rospy.init_node('imu', anonymous=True)
#    rate = rospy.Rate(10) # 10hz
#    while not rospy.is_shutdown():
#        hello_str = "hello world %s" % rospy.get_time()
#        rospy.loginfo(hello_str)
#        pub.publish(hello_str)
#        rate.sleep()

def millidegrees_to_radians(value):
    return (value / 1000.0) * (math.pi / 180.0)

def millig_to_meter(value):
    return (value / 1000.0) * 9.81

def set_all_covariance(imu_msg, covariance_matrix):
    imu_msg.orientation_covariance = covariance_matrix
    imu_msg.angular_velocity_covariance = covariance_matrix
    imu_msg.linear_acceleration_covariance = covariance_matrix

if __name__ == '__main__':
    try:
        rospy.init_node('ahrs8_node')
        rospy.loginfo("AHRS8 node started successfully")
        
        # Try to auto-detect device, fallback to hardcoded default
        auto_detected_port = find_sparton_device()
        if auto_detected_port:
            default_port = auto_detected_port
            rospy.loginfo("Auto-detected Sparton AHRS8 at: {}".format(default_port))
        else:
            # Fallback defaults for different platforms
            default_port = '/dev/tty.usbserial-FTFUT9EB'  # macOS default
            rospy.logwarn("Could not auto-detect device, using default: {}".format(default_port))
        
        default_baud = 115200
        default_frameid = 'ahrs8_imu'
        default_polling_rate = 10  # Hz

        compass_port = rospy.get_param('~port', default_port)
        compass_baud = rospy.get_param('~baud', default_baud)
        compass_frame = rospy.get_param('~frame_id', default_frameid)
        polling_rate = rospy.get_param('~polling_rate', default_polling_rate)
        
        imu_pub = rospy.Publisher('imu', Imu, queue_size=10)
        eul_pub = rospy.Publisher('imu/euler', Twist, queue_size=10)
        imu_msg = Imu()
        eul_msg = Twist()
        global roll, pitch, yaw
        imu_msg.header.frame_id = compass_frame

        default_covariance_matrix = [1e-6] * 9

        set_all_covariance(imu_msg, default_covariance_matrix)

        compass_serial = serial.Serial(compass_port, compass_baud, timeout=1)

        try:
            compass_serial.write(b'\x13')
            compass_serial.write(b'$xxHDM\r\n')
            compass_serial.write(b'printmask 0 set drop\r\n')
            compass_serial.write(b'printmodulus 0 set drop\r\n')
            compass_serial.write(b'printtrigger 0 set drop\r\n')
            rospy.sleep(0.1)
            compass_serial.write(b'\x11')
            rospy.sleep(0.1)
            compass_serial.flushInput()
            compass_serial.flushOutput()
            rospy.sleep(0.1)
        except serial.SerialException:
            rospy.logerr('AHRS-8: Serial communications not opened properly.')

        rospy.loginfo('AHRS-8: Output reset, beginning to retrieve data.')
        
        # Set up rate control
        rate = rospy.Rate(polling_rate)
        rospy.loginfo('AHRS-8: Polling rate set to {} Hz'.format(polling_rate))

        while not rospy.is_shutdown():
            compass_serial.write(b'$PSPA,G\r\n')
            response = compass_serial.readline()
            if verify_checksum(response):
                populate_G(response, imu_msg)
            else:
                rospy.logerr('AHRS-8: Bad checksum, skipping dataset.')
                continue

            compass_serial.write(b'$PSPA,QUAT\r\n')
            response = compass_serial.readline()
            if verify_checksum(response):
                populate_QUAT(response, imu_msg)
            else:
                rospy.logerr('AHRS-8: Bad checksum, skipping dataset.')
                continue

            compass_serial.write(b'$PSPA,A\r\n')
            response = compass_serial.readline()
            if verify_checksum(response):
                populate_A(response, imu_msg)
            else:
                rospy.logerr('AHRS-8: Bad checksum, skipping dataset.')
                continue

            imu_msg.header.stamp = rospy.Time.now()
            imu_pub.publish(imu_msg)
            orientation_q = imu_msg.orientation
            orientation_list = [orientation_q.x, orientation_q.y, orientation_q.z, orientation_q.w]
            (roll, pitch, yaw) = euler_from_quaternion (orientation_list)
            eul_msg.linear.x = math.degrees(roll)
            eul_msg.linear.y = math.degrees(pitch)
            eul_msg.linear.z = math.degrees(yaw)
            eul_pub.publish(eul_msg)
            
            # Sleep according to polling rate
            rate.sleep()

    except Exception as e:
        rospy.logerr("AHRS8 error: {}".format(str(e)))
        import traceback
        rospy.logerr("Traceback: {}".format(traceback.format_exc()))
