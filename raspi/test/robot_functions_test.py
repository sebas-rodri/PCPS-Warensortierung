import unittest

from raspi.src.robot_functions import Robot


class RobotFunctionTest(unittest.TestCase):
    def testReset(self):
        arm = Robot()
        arm.reset()
        is_successful = input("Has Robot successfully reset? (Y/N) ->")
        self.assertEqual("Y", is_successful)

    def testMoveToBox1(self):
        arm = Robot()
        arm.itemToBoxOne()
        is_successful = input("Has Robot moved item to box 1? (Y/N) ->")
        self.assertEqual("Y", is_successful)

    def testMoveToBox2(self):
        arm = Robot()
        arm.itemToBoxTwo()
        is_successful = input("Has Robot moved item to box 2? (Y/N) ->")
        self.assertEqual("Y", is_successful)

    def testMoveAll(self):
        arm = Robot()
        arm.itemToBoxOne()
        arm.itemToBoxTwo()
        arm.reset()
        is_successful = input("Has Robot moved to scale, box 1, scale, box 2? (Y/N) ->")
        self.assertEqual("Y", is_successful)


if __name__ == '__main__':
    unittest.main()
