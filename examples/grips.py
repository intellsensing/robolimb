"""
Grips
=====
A simple console application that takes input from the user in orderto execute
a specified grip. The grip is executed at maximum speed and in a single phase
(i.e., there is no differentation between pre-grasp and grasp).
"""

import sys
import time
from can.interfaces.pcan import PCANBasic as pcan
from six.moves import input

from robolimb import RoboLimbCAN as RoboLimb

grips = {1: "cylindrical", 2: "lateral", 3: "tripod", 4: "tripod_ext",
         5: "pinch", 6: "pinch_ext", 7: "pointer", 8: "thumbs_up", 9: "horns"}


class RoboLimbGrip(RoboLimb):
    def __init__(self,
                 def_vel=297,
                 read_rate=0.02,
                 channel=pcan.PCAN_USBBUS1,
                 b_rate=pcan.PCAN_BAUD_1M,
                 hw_type=pcan.PCAN_TYPE_ISA,
                 io_port=0x3BC,
                 interrupt=3):
        super().__init__(
            def_vel,
            read_rate,
            channel,
            b_rate,
            hw_type,
            io_port,
            interrupt)

        self.grip = None

    def execute(self, grip):
        """Performs grip at maximum velocity."""
        velocity = 297
        if grip == 'open':
            self.open_fingers(velocity=velocity)
            time.sleep(1)
            self.grip = 'open'
        elif grip == 'cylindrical':
            # Preparation
            [self.open_finger(i, velocity=velocity) for i in range(1, 6)]
            time.sleep(0.2)
            self.close_finger(6, velocity=velocity)
            time.sleep(1.3)
            # Execution
            self.stop_all()
            self.close_fingers(velocity=velocity, force=True)
            time.sleep(1)
            self.grip = 'cylindrical'
        elif grip == 'lateral':
            # Preparation
            [self.open_finger(i, velocity=velocity) for i in range(1, 4)]
            time.sleep(0.2)
            self.open_finger(6, velocity=velocity, force=True)
            time.sleep(0.1)
            [self.stop_finger(i) for i in range(2, 4)]
            [self.close_finger(i, velocity=velocity) for i in range(2, 6)]
            time.sleep(1.2)
            # Execution
            self.stop_all()
            self.close_finger(1, velocity=velocity, force=True)
            time.sleep(1)
            self.grip = 'lateral'
        elif grip == 'tripod':
            # Preparation
            [self.open_finger(i, velocity=velocity) for i in range(1, 4)]
            time.sleep(0.1)
            [self.stop_finger(i) for i in range(1, 4)]
            [self.close_finger(i, velocity=velocity) for i in range(4, 7)]
            time.sleep(1.4)
            # Execution
            self.stop_all()
            [self.close_finger(i, velocity=velocity, force=True)
             for i in range(1, 4)]
            time.sleep(1)
            self.grip = 'tripod'
        elif grip == 'tripod_ext':
            # Preparation
            self.open_fingers(velocity=velocity)
            time.sleep(0.1)
            self.stop_fingers()
            self.close_finger(6, velocity=velocity)
            time.sleep(1.4)
            # Execution
            self.stop_all()
            [self.close_finger(i, velocity=velocity, force=True)
             for i in range(1, 4)]
            time.sleep(1)
            self.grip = 'tripod_ext'
        elif grip == 'pinch':
            # Preparation
            [self.open_finger(i, velocity=velocity) for i in range(1, 3)]
            time.sleep(0.1)
            [self.close_finger(i, velocity=velocity) for i in range(3, 7)]
            time.sleep(1.3)
            self.stop_finger(6)
            self.open_finger(6)
            time.sleep(0.1)
            self.stop_finger(6)
            # Execution
            self.stop_all()
            [self.close_finger(i, velocity=velocity, force=True)
             for i in range(1, 4)]
            time.sleep(1)
            self.grip = 'pinch'
        elif grip == 'pinch_ext':
            # Preparation
            [self.open_finger(i, velocity=velocity) for i in range(1, 6)]
            time.sleep(0.1)
            self.close_finger(6, velocity=velocity)
            time.sleep(1.3)
            self.stop_finger(6)
            self.open_finger(6)
            time.sleep(0.1)
            self.stop_finger(6)
            # Execution
            self.stop_all()
            [self.close_finger(i, velocity=velocity, force=True)
             for i in range(1, 3)]
            time.sleep(1)
            self.grip = 'pinch_ext'
        elif grip == 'pointer':
            # Preparation
            [self.open_finger(i, velocity=velocity) for i in range(1, 3)]
            time.sleep(0.1)
            self.open_finger(6, velocity=velocity)
            time.sleep(1.4)
            # Execution
            self.stop_all()
            [self.close_finger(i, velocity=velocity, force=True)
             for i in [1, 3, 4, 5]]
            time.sleep(1)
            self.grip = 'pointer'
        elif grip == 'thumbs_up':
            # Preparation
            self.open_finger(6, velocity=velocity)
            time.sleep(0.1)
            [self.close_finger(i, velocity=velocity) for i in range(1, 6)]
            time.sleep(1.4)
            # Execution
            self.stop_all()
            self.open_finger(1, velocity=velocity, force=True)
            time.sleep(1)
            self.grip = 'thumbs_up'
        elif grip == 'horns':
            # Preparation
            [self.open_finger(i, velocity=velocity) for i in range(1, 3)]
            time.sleep(0.1)
            self.open_finger(6, velocity=velocity)
            time.sleep(1.4)
            # Execution
            self.stop_all()
            [self.close_finger(i, velocity=velocity, force=True)
             for i in [1, 3, 4]]
            time.sleep(1)
            self.grip = 'horns'


class RoboLimbGripExample(object):
    def __init__(self):
        self.r = RoboLimbGrip()

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

                self.r.execute(grips[grip_id])

                _ = input('Press any key to open')
                self.r.execute('open')

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
    ex = RoboLimbGripExample()
    ex.start()
    ex.main()
