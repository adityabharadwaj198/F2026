import sys
import time
import threading
import cflib.crtp
from cflib.crazyflie import Crazyflie
# URI for your LiteWing drone (ESP-Drone firmware listens on UDP port 2390)
DRONE_URI = "udp://192.168.43.42:2390"
# Initialize CRTP drivers
cflib.crtp.init_drivers()
# Basic flight test
print("Hello World to LiteWing")
# Create Crazyflie instance
cf = Crazyflie(rw_cache='./cache')
# open_link() returns immediately and does not raise on failure,
# so wait for the connected / connection_failed callbacks instead
connected = threading.Event()
cf.link_established.add_callback(lambda uri: print("Got a reply from the drone, downloading parameters..."))
cf.connected.add_callback(lambda uri: connected.set())
cf.connection_failed.add_callback(lambda uri, msg: print("Connection failed:", msg))
# Connect to the drone
print("Connecting to drone...")
cf.open_link(DRONE_URI)
if not connected.wait(timeout=15):
    print("Could not connect. Is this computer on the drone's Wi-Fi (IP 192.168.43.x)?")
    cf.close_link()
    sys.exit(1)
print("Connected to drone. Waiting for stability...")
time.sleep(1.0)  # Wait after connection
# First send zero setpoint to unlock safety
print("Sending zero setpoint to unlock safety...")
cf.commander.send_setpoint(0, 0, 0, 0)
time.sleep(0.1)
# Flight parameters
roll = 0.0
pitch = 0.0
yaw = 0
thrust = 10000  # Thrust value is 10000 minimum and 60000 maximum
# Start motors. Setpoints must be sent continuously - the firmware
# stops the motors if it doesn't receive one for ~500 ms
print("Starting motors at minimum speed...")
for _ in range(20):  # 2 seconds at 10 Hz
    cf.commander.send_setpoint(roll, pitch, yaw, thrust)
    time.sleep(0.1)
# Stop the motors
print("Stopping motors...")
cf.commander.send_setpoint(0, 0, 0, 0)
time.sleep(0.1)
# Close the connection
cf.close_link()
print("Test complete")
