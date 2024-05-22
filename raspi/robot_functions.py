from wlkata_mirobot import WlkataMirobot
import time


class Robot(WlkataMirobot):
    def __init__(self, *device_args, **device_kwargs):
        """
        Initializes an instance of the robot and brings it to home position

        :param device_args:
        :param device_kwargs:
        """
        super().__init__(*device_args, **device_kwargs)
        self.home()

    def reset(self):
        """
        Resets the robot to its home position.
        :return: 1 if successful
        """
        self.home()
        return 1

    def itemToBoxOne(self):
        """
        Picks up item from scale and moves item to box one.
        :return: 1
        """
        # Move to scale
        self.set_tool_pose(200, 20, 230)
        # Pickup item
        self.pump_suction()
        # Move to box 1
        self.set_tool_pose(-200, 10, 230)
        # Release item
        self.pump_blowing()
        time.sleep(1)
        # switch pump off
        self.pump_off()
        return 1


    def itemToBoxTwo(self):
        """
        Picks up item from scale and moves item to box two.
        :return:
        """
        # Move to scale
        self.set_tool_pose(200, 20, 230)
        # Pickup item
        self.pump_suction()
        # Move to box 2
        self.set_tool_pose(-200, 30, 230)
        # Release item
        self.pump_blowing()
        time.sleep(1)
        # switch pump off
        self.pump_off()
        return 1
