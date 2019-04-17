import threading

class RepeatedTimer(object):
    """
    A simple timer implementation that repeats itself.

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
    def __init__(self, target, interval, name=None, args=[], kwargs={}):

        self.target = target
        self.interval = interval
        self.name = name
        self.args = args
        self.kwargs = kwargs

        self._thread = None
        self._event = None
        self._bStarted = False

    def _run(self):
        """Runs the thread that emulates the timer."""
        while not self._event.wait(self.interval):
            self.target(*self.args, **self.kwargs)

    def start(self):
        """Starts the timer."""
        if (self._thread == None):
            self._event = threading.Event()
            self._thread = threading.Thread(None, self._run, self.name)
            self._thread.start()

    def stop(self):
        """Stops the timer."""
        if (self._thread != None):
            self._event.set()
            self._thread = None
