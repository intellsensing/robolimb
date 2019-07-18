"""
Preshapes
=========
A simple console application that takes input from the user in order to execute
a specified grip pre-shape. The pre-shape is executed at maximum speed and
then the user is prompted to input a desired velocity for closing/opening the
relevant fingers or change posture.
"""

import sys
import time
from can.interfaces.pcan.basic import PCAN_USBBUS1, PCAN_BAUD_1M, PCAN_TYPE_ISA
from six.moves import input

from robolimb import RoboLimbCAN as RoboLimb

grips = {1: "cylindrical", 2: "lateral", 3: "tripod", 4: "tripod_ext",
         5: "pinch", 6: "pinch_ext", 7: "pointer", 8: "thumbs_up", 9: "horns"}


class RoboLimbPreshape(RoboLimb):
    def __init__(self,
                 def_vel=297,
                 channel=PCAN_USBBUS1,
                 b_rate=PCAN_BAUD_1M,
                 hw_type=PCAN_TYPE_ISA,
                 io_port=0x3BC,
                 interrupt=3):
        super().__init__(
            def_vel,
            channel,
            b_rate,
            hw_type,
            io_port,
            interrupt)

        self.grip = None

    def preshape(self, grip):
        """Performs grip pre-shape at maximum velocity."""
        velocity = 297
        if grip == 'cylindrical':
            [self.open_finger(i, velocity=velocity) for i in range(1, 6)]
            time.sleep(0.2)
            self.close_finger(6, velocity=velocity)
            time.sleep(1.3)
            self.stop_all()
            self.grip = 'cylindrical'
        elif grip == 'lateral':
            [self.open_finger(i, velocity=velocity) for i in range(1, 4)]
            time.sleep(0.2)
            self.open_finger(6, velocity=velocity, force=True)
            time.sleep(0.1)
            [self.stop_finger(i) for i in range(2, 4)]
            [self.close_finger(i, velocity=velocity) for i in range(2, 6)]
            time.sleep(1.2)
            self.stop_all()
            self.grip = 'lateral'
        elif grip == 'tripod':
            [self.open_finger(i, velocity=velocity) for i in range(1, 4)]
            time.sleep(0.1)
            [self.stop_finger(i) for i in range(1, 4)]
            [self.close_finger(i, velocity=velocity) for i in range(4, 7)]
            time.sleep(1.4)
            self.stop_all()
            self.grip = 'tripod'
        elif grip == 'tripod_ext':
            self.open_fingers(velocity=velocity)
            time.sleep(0.1)
            self.stop_fingers()
            self.close_finger(6, velocity=velocity)
            time.sleep(1.4)
            self.stop_all()
            self.grip = 'tripod_ext'
        elif grip == 'pinch':
            [self.open_finger(i, velocity=velocity) for i in range(1, 3)]
            time.sleep(0.1)
            [self.close_finger(i, velocity=velocity) for i in range(3, 7)]
            time.sleep(1.3)
            self.stop_finger(6)
            self.open_finger(6)
            time.sleep(0.1)
            self.stop_finger(6)
            self.stop_all()
            self.grip = 'pinch'
        elif grip == 'pinch_ext':
            [self.open_finger(i, velocity=velocity) for i in range(1, 6)]
            time.sleep(0.1)
            self.close_finger(6, velocity=velocity)
            time.sleep(1.3)
            self.stop_finger(6)
            self.open_finger(6)
            time.sleep(0.1)
            self.stop_finger(6)
            self.stop_all()
            self.grip = 'pinch_ext'
        elif grip == 'pointer':
            [self.open_finger(i, velocity=velocity) for i in range(1, 3)]
            time.sleep(0.1)
            self.open_finger(6, velocity=velocity)
            time.sleep(1.4)
            self.stop_all()
            self.grip = 'pointer'
        elif grip == 'thumbs_up':
            self.open_finger(6, velocity=velocity)
            time.sleep(0.1)
            [self.close_finger(i, velocity=velocity) for i in range(1, 6)]
            time.sleep(1.4)
            self.stop_all()
            self.grip = 'thumbs_up'
        elif grip == 'horns':
            [self.open_finger(i, velocity=velocity) for i in range(1, 3)]
            time.sleep(0.1)
            self.open_finger(6, velocity=velocity)
            time.sleep(1.4)
            self.stop_all()
            self.grip = 'horns'

    def close_grip(self, velocity):
        if self.grip == 'cylindrical':
            self.close_fingers(velocity=velocity, force=True)
            time.sleep(1)
        if self.grip == 'lateral':
            self.close_finger(1, velocity=velocity, force=True)
            time.sleep(1)
        if self.grip == 'tripod':
            [self.close_finger(i, velocity=velocity, force=True)
             for i in range(1, 4)]
            time.sleep(1)
        if self.grip == 'tripod_ext':
            [self.close_finger(i, velocity=velocity, force=True)
             for i in range(1, 4)]
            time.sleep(1)
        if self.grip == 'pinch':
            [self.close_finger(i, velocity=velocity, force=True)
             for i in range(1, 4)]
            time.sleep(1)
        if self.grip == 'pinch_ext':
            [self.close_finger(i, velocity=velocity, force=True)
             for i in range(1, 3)]
            time.sleep(1)
        if self.grip == 'pointer':
            [self.close_finger(i, velocity=velocity, force=True)
             for i in [1, 3, 4, 5]]
            time.sleep(1)
        if self.grip == 'thumbs_up':
            self.open_finger(1, velocity=velocity, force=True)
            time.sleep(1)
        if self.grip == 'horns':
            [self.close_finger(i, velocity=velocity, force=True)
             for i in [1, 3, 4]]
            time.sleep(1)

    def open_grip(self, velocity):
        if self.grip == 'cylindrical':
            self.open_fingers(velocity=velocity, force=True)
            time.sleep(1)
        if self.grip == 'lateral':
            self.open_finger(1, velocity=velocity, force=True)
            time.sleep(1)
        if self.grip == 'tripod':
            [self.open_finger(i, velocity=velocity, force=True)
             for i in range(1, 4)]
            time.sleep(1)
        if self.grip == 'tripod_ext':
            [self.open_finger(i, velocity=velocity, force=True)
             for i in range(1, 4)]
            time.sleep(1)
        if self.grip == 'pinch':
            [self.open_finger(i, velocity=velocity, force=True)
             for i in range(1, 4)]
            time.sleep(1)
        if self.grip == 'pinch_ext':
            [self.open_finger(i, velocity=velocity, force=True)
             for i in range(1, 3)]
            time.sleep(1)
        if self.grip == 'pointer':
            [self.open_finger(i, velocity=velocity, force=True)
             for i in [1, 3, 4, 5]]
            time.sleep(1)
        if self.grip == 'thumbs_up':
            self.close_finger(1, velocity=velocity, force=True)
            time.sleep(1)
        if self.grip == 'horns':
            [self.open_finger(i, velocity=velocity, force=True)
             for i in [1, 3, 4]]
            time.sleep(1)


class RoboLimbPreshapeExample(object):
    def __init__(self):
        self.r = RoboLimbPreshape()

    def start(self):
        self.r.start()
        self.r.open_all()
        time.sleep(1.5)

    def main(self):
        try:
            while(True):
                grip_id = -1
                while grip_id not in range(1, 10):
                    grip_id = int(input("Select grip (1:cylindrical, " +
                                        "2:lateral, 3:tripod, " +
                                        "4: tripod extended, 5:pinch " +
                                        "6:pinch extended, 7:pointer " +
                                        "8:thumbs_up, 9:horns, 0:exit)\n"))
                    self.check_exit_application(grip_id)

                self.r.preshape(grips[grip_id])
                vel = 1
                while vel > 0:
                    vel = int(input("Select closing velocity (10-297) or " +
                                    "press 0 to change posture\n"))
                    if vel == 0:
                        self.r.open_all()
                        break
                    else:
                        self.r.close_grip(vel)

                    vel = int(input("Select opening velocity (10-297) or " +
                                    "press 0 to change posture\n"))
                    if vel == 0:
                        self.r.open_all()
                    else:
                        self.r.open_grip(vel)

        except KeyboardInterrupt:
            self.r.stop_all()
            self.exit_application()

    def check_exit_application(self, input):
        if input == 0:
            self.exit_application()

    def exit_application(self):
        print("Exiting...")
        self.r.open_all()
        time.sleep(1)
        self.r.close_finger(1)
        time.sleep(1)
        self.r.stop()
        sys.exit()


if __name__ == "__main__":
    ex = RoboLimbPreshapeExample()
    ex.start()
    ex.main()
