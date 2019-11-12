# Robolimb
Control interface for the Touch Bionics (Össur) RoboLimb prosthetic/robotic hand in Python. 

Currently the CAN bus communications is only supported. 

The code provides a basic, low-level interface for controlling the hand digits and reading incoming CAN messages. Some usage examples including grasp control can be found in [examples](examples).

For technical details please refer to the device user manual which can be found in [user_manual](user_manual).

Here is a minimal example that initiates a connection to the hand, sends a close command for the index finger and closes the connection with the hand:

```python
import time
from robolimb import RoboLimbCAN as RL

r = RL()
r.start()
r.close_finger(2)
time.sleep(1.5)
r.stop()
```

## Dependencies
* Python >= 3.6 (other versions have not been tested and may or may not work)
* [python-can](https://pypi.python.org/pypi/python-can/) 

## Notes
* Only tested using the [PCAN-USB](https://www.peak-system.com/PCAN-USB.199.0.html?&L=1) interface. Device drivers need to be installed (available for Windows and Linux, see previous link). 
* CAN feedback messages do not seem to be very reliable. There also seems to be a delay between finger state and feedback messages. 
