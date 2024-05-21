'''
Position control, point to point (P2P)
'''
import time
from wlkata_mirobot import WlkataMirobot

# create instance of microbot
arm = WlkataMirobot()
# Return to mechanical zero Homing (synchronous mode)
arm.home()

print("Move to target point A")
arm.set_tool_pose(200,  20, 230)
print(f"Current position of robot -> {arm.pose}")
time.sleep(1)

print("Move to target point B")
arm.set_tool_pose(200,  20, 150)
print(f"Current position of robot -> {arm.pose}")
time.sleep(1)

print("Move to target point C with specified angle")
arm.set_tool_pose(150,  -20,  230, roll=30.0, pitch=0, yaw=45.0)
print(f"Current position of robot -> {arm.pose}")

arm.home()