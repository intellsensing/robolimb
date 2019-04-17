from robolimb.utils import RepeatedTimer
import threading
import time
import math


def test_repeated_timer():
    class TestClass(object):
        """A test class with a variable that is incremented by a constant value
        every time the target function is called.
        """

        def __init__(self, interval, constant):
            self.rt = RepeatedTimer(self.add_constant, interval,
                                    args=[constant])
            self.i = 0

        def start(self):
            self.rt.start()

        def stop(self):
            self.rt.stop()

        def add_constant(self, constant):
            self.i += constant

    interval = 0.05
    exec_time = 0.5
    constant = 1

    tc = TestClass(interval, constant=constant)
    tc.start()
    time.sleep(exec_time)
    tc.stop()
    assert(tc.i == constant * (math.floor(exec_time / interval) - 1))
