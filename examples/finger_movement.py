"""
Finger movement
===============
A simple console application that takes input from the user in order to move a
single degree-of-freedom at specified velocity and for specified time.
"""

import sys
import time
import threading
from robolimb import RoboLimbCAN as RoboLimb
from six.moves import input

class RoboLimbFingerExample(object):
    def __init__(self):
        self.r = RoboLimb()

    def start(self):
        self.r.start()
        self.r.open_all()
        time.sleep(1.5)

    def main(self):
        try:
            while(True):
                finger, action, vel, time_ = -1, -1, -1, -1
                while finger not in range(1, 7):
                    finger = int(input("Select finger (1:thumb, " +
                                       "2:index, 3:middle, 4:ring, " +
                                       "5:little, 6:thumb rotation, " +
                                       "0:exit)\n"))
                    self.check_exit_application(finger)

                while action not in range(1, 3):
                    action = int(input("Select action (1:close, " +
                                       "2:open) \n"))

                while vel not in range(10, 298):
                    vel = int(input("Select velocity (10-297) \n"))

                while time_ < 0:
                    time_ = float(input("Select action time (ms) \n"))

                if action == 1:
                    self.r.close_finger(finger, vel)
                    threading.Timer(
                        time_ * 1e-3, self.r.stop_finger, [finger, vel]).start()
                elif action == 2:
                    self.r.open_finger(finger, vel)
                    threading.Timer(
                        time_ * 1e-3, self.r.stop_finger, [finger, vel]).start()

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
    # Support Python 2 and 3 input
    input = input
    if sys.version_info[:2] <= (2, 7):
        input = raw_input

    ex = RoboLimbFingerExample()
    ex.start()
    ex.main()
