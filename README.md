# Robolimb
Control interface for the Touch Bionics (Össur) RoboLimb prosthetic/robotic hand in Python. 

Currently the CAN bus communications is only supported. 

The code provides a basic, low-level interface for controlling the hand digits and reading incoming CAN messages. Some usage examples including grasp control can be found in [examples](examples).

For technical details please refer to the device user manual which can be found in [user_manual](user_manual).

Here is a minimal example:
```python
import time
from robolimb import RoboLimbCAN

r = RoboLimbCAN()
r.start()
r.close_finger(2)
time.sleep(1.5)
r.stop()
```

## Dependencies
* Python >= 3.6 (other versions have not been tested may or may not work)
* [python-can](https://pypi.python.org/pypi/python-can/) 
