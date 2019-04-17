import threading
import time


class RepeatedTimer(object):
    """
    A simple timer implementation that repeats itself and avoids drift over
    time.

    Implementation based on https://stackoverflow.com/a/40965385.

    Parameters
    ----------
    target : callable
        Target function
    interval : float
        Target function repetition interval
    name : str, optional (default: None)
        Thread name
    args : list
        Non keyword-argument list for target function
    kwargs : key,value mappings
        Keyword-argument dict for target function
    """

    def __init__(self, target, interval, args=(), kwargs={}):

        self.target = target
        self.interval = interval
        self.args = args
        self.kwargs = kwargs

        self._timer = None
        self._is_running = False
        self._next_call = time.time()
        self.start()

    def _run(self):
        self._is_running = False
        self.start()
        self.target(*self.args, **self.kwargs)

    def start(self):
        if not self._is_running:
            self._next_call += self.interval
            self._timer = threading.Timer(self._next_call - time.time(),
                                          self._run)
            self._timer.start()
            self._is_running = True

    def stop(self):
        self._timer.cancel()
        self._is_running = False
