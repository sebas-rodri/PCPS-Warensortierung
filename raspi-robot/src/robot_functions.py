import time
import wlkata_mirobot

POSITION_SCALE = (70, -230, 50)
POSITION_BOX_1 = (50, 240, 100)
POSITION_BOX_2 = (-55, 210, 100)
POSITION_INPUT_BOX = (200, -150, 18)


class Robot(wlkata_mirobot.WlkataMirobot):

    def __init__(self, *device_args, **device_kwargs) -> None:
        """
        Initializes an instance of the robot and brings it to home position

        :param device_args: Arguments passed to the parent class constructor
        :param device_kwargs: Keyword arguments passed to the parent class constructor
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
        # Move to box 1 up
        self.set_tool_pose(POSITION_BOX_1[0], POSITION_BOX_1[1], POSITION_BOX_1[2] + 100)
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
        self.pump_off()
        time.sleep(1)
        # Move to box 2 up
        self.set_tool_pose(POSITION_BOX_2[0], POSITION_BOX_2[1], POSITION_BOX_2[2] + 100)
        # return to neutral position
        self.go_to_zero()

    def getRobotStatus(self):
        """
        Gets the status of the robot.

        :return: The status of the robot.
        """
        return self.get_status()

    def get_package(self) -> None:
        """
        Picks up item from the input_Box and moves item to the scale.

        :return: None
        """

        # Move to Input Box
        self.set_tool_pose(POSITION_INPUT_BOX[0], POSITION_INPUT_BOX[1], POSITION_INPUT_BOX[2] + 100)
        self.set_tool_pose(POSITION_INPUT_BOX[0], POSITION_INPUT_BOX[1], POSITION_INPUT_BOX[2])
        # Pickup Box
        self.pump_suction()
        time.sleep(1)
        # Move Up
        self.set_tool_pose(POSITION_INPUT_BOX[0], POSITION_INPUT_BOX[1], POSITION_INPUT_BOX[2] + 100)
        # Move to scale
        self.set_tool_pose(POSITION_SCALE[0], POSITION_SCALE[1], POSITION_SCALE[2] + 100)
        self.set_tool_pose(POSITION_SCALE[0], POSITION_SCALE[1], POSITION_SCALE[2])
        # Release Item
        self.pump_blowing()
        self.pump_off()
        # Move up
        self.set_tool_pose(POSITION_SCALE[0], POSITION_SCALE[1], POSITION_SCALE[2] + 100)
