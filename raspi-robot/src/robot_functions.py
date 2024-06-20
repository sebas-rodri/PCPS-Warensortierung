import time
import wlkata_mirobot

POSITION_SCALE = (70, -230, 50)
POSITION_BOX_1 = (50, 240, 100)
POSITION_BOX_2 = (-150, 240, 100)


class Robot(wlkata_mirobot.WlkataMirobot):
    """
    Initializes an instance of the robot and brings it to home position

    :param device_args: Arguments passed to the parent class constructor
    :param device_kwargs: Keyword arguments passed to the parent class constructor
    """
    def __init__(self, *device_args, **device_kwargs) -> None:
        """
        Initializes an instance of the robot and brings it to home position

        :param device_args:
        :param device_kwargs:
        """
        super().__init__(*device_args, **device_kwargs)
        self.home()

    def reset(self) -> None:
        """
        Resets the robot to its zero position.

        :return: None
        """
        self.go_to_zero()

    def itemToBoxOne(self) -> None:
        """
        Picks up item from scale and moves item to box one.

        :return: None
        """
        # Move to scale
        self.set_tool_pose(POSITION_SCALE[0], POSITION_SCALE[1], POSITION_SCALE[2] + 100)
        self.set_tool_pose(POSITION_SCALE[0], POSITION_SCALE[1], POSITION_SCALE[2])
        # Pickup item
        self.pump_on()
        # Move up
        self.set_tool_pose(POSITION_SCALE[0], POSITION_SCALE[1], POSITION_SCALE[2] + 100)
        # Move to box 1 up
        self.set_tool_pose(POSITION_BOX_1[0], POSITION_BOX_1[1], POSITION_BOX_1[2] + 100)
        # Move to box 1
        self.set_tool_pose(POSITION_BOX_1[0], POSITION_BOX_1[1], POSITION_BOX_1[2])
        # Release item
        self.pump_off()
        time.sleep(1)
        # return to neutral position
        self.go_to_zero()

    def itemToBoxTwo(self) -> None:
        """
        Picks up item from scale and moves item to box two.

        :return: None
        """
        # Move to scale
        self.set_tool_pose(POSITION_SCALE[0], POSITION_SCALE[1], POSITION_SCALE[2] + 100)
        self.set_tool_pose(POSITION_SCALE[0], POSITION_SCALE[1], POSITION_SCALE[2])
        # Pickup item
        self.pump_suction()
        time.sleep(2)
        # Move up
        self.set_tool_pose(POSITION_SCALE[0], POSITION_SCALE[1], POSITION_SCALE[2] + 100)
        # Move to box 2 up
        self.set_tool_pose(POSITION_BOX_2[0], POSITION_BOX_2[1], POSITION_BOX_2[2] + 100)
        # Move down
        self.set_tool_pose(POSITION_BOX_2[0], POSITION_BOX_2[1], POSITION_BOX_2[2])
        # Release item
        self.pump_blowing()
        time.sleep(1)
        # return to neutral position
        self.go_to_zero()

    def getRobotStatus(self):
        """
        Gets the status of the robot.

        :return: The status of the robot.
        """
        return self.get_status()
