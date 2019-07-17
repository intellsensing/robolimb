import threading

from can.interfaces.pcan.basic import (PCANBasic, PCAN_USBBUS1, PCAN_BAUD_1M,
                                       PCAN_TYPE_ISA, PCAN_ERROR_QRCVEMPTY,
                                       PCAN_ERROR_OK, TPCANMsg,
                                       PCAN_MESSAGE_STANDARD)
from .utils import RepeatedTimer

# Refer to robo-limb manual for definition of number codes used below
N_DOF = 6
FINGERS = {'thumb': 1, 'index': 2, 'middle': 3, 'ring': 4,
           'little': 5, 'rotator': 6}
ACTIONS = {'stop': 0, 'close': 1, 'open': 2}
STATUS = {0: 'stop', 1: 'closing', 2: 'opening', 3: 'stalled close',
          4: 'stalled open'}


class RoboLimbCAN(object):
    """ Robo-limb control via CAN bus interface.

    Parameters
    ----------
    def_vel : int, optional (default: 297)
        Default velocity for finger control. Has to be in range (10,297).
    read_rate : float, optional (default: 0.02)
        Update rate for incoming CAN messages [s]
    channel : pcan definition, optional (default: PCAN_USBBUS1)
        CAN communication channel
    b_rate : pcan definition, optional (default: PCAN_BAUD_1M)
        CAN baud rate
    hw_type : pcan definition, optional (default: PCAN_TYPE_ISA)
        CAN hardware type
    io_port : hex,  (default: 0x3BC)
        CAN input-output port
    interrupt : int, optional (default: 3)
        CAN interrupt handler

    Attributes
    ----------
    finger_status : list
        Finger status
    finger_current : list
        Finger currents
    """

    def __init__(self,
                 def_vel=297,
                 read_rate=0.02,
                 channel=PCAN_USBBUS1,
                 b_rate=PCAN_BAUD_1M,
                 hw_type=PCAN_TYPE_ISA,
                 io_port=0x3BC,
                 interrupt=3):
        self.channel = channel
        self.b_rate = b_rate
        self.hw_type = hw_type
        self.io_port = io_port
        self.interrupt = interrupt
        self.def_vel = def_vel
        self.read_rate = read_rate

        self.finger_status = [None] * N_DOF
        self.finger_current = [None] * N_DOF

        self.msg_read = RepeatedTimer(self.__read_messages, self.read_rate)
        self.__is_moving = False

    def start(self):
        """Starts the connection."""
        self.bus = PCANBasic()
        self.bus.Initialize(Channel=self.channel, Btr0Btr1=self.b_rate,
                            HwType=self.hw_type, IOPort=self.io_port,
                            Interrupt=self.interrupt)
        self.msg_read.start()

    def stop(self):
        """Stops reading incoming CAN messages and shuts down the
        connection."""
        self.msg_read.stop()
        self.bus.Uninitialize(Channel=self.channel)

    def open_finger(self, finger, velocity=None, force=True):
        """Opens single digit at specified velocity.

        Parameters
        ----------
        finger : int or str
            Finger ID
        velocity : int, optional
            Desired velocity.  Has to be in range (10,297). If not provided, the
            default velocity will be used.
        force : boolean, optional (default: True)
            If False and the finger status is ```opening``` or ```stalled
            open``` the command will not be sent.
        """
        velocity = self.def_vel if velocity is None else int(velocity)
        finger = self.__get_finger_id(finger)
        if self.finger_status[finger - 1] in ['opening',
                                              'stalled open'] and force is False:
            pass
        else:
            self.__motor_command(finger, ACTIONS['open'], velocity)

    def close_finger(self, finger, velocity=None, force=True):
        """Closes single digit at specified velocity.

        Parameters
        ----------
        finger : int or str
            Finger ID
        velocity : int, optional
            Desired velocity.  Has to be in range (10,297). If not provided, the
            default velocity will be used.
        force : boolean, optional (default: True)
            If False and the finger status is ```closing``` or ```stalled
            close``` the command will not be sent.

        """
        velocity = self.def_vel if velocity is None else int(velocity)
        finger = self.__get_finger_id(finger)
        if self.finger_status[finger - 1] in ['closing',
                                              'stalled close'] and force is False:
            pass
        else:
            self.__motor_command(finger, ACTIONS['close'], velocity)

    def stop_finger(self, finger, force=True):
        """Stops execution of digit movement.

        Parameters
        ----------
        finger : int or str
            Finger ID
        force : boolean, optional (default: True)
            If the finger status is ```stop``` the command will not be sent.
        """
        finger = self.__get_finger_id(finger)
        if self.finger_status[finger - 1] is 'stop' and force is False:
            pass
        elif self.finger_status[finger - 1] in [
                'stalled open', 'stalled closed'] and force is False:
            self.finger_status[finger - 1] = 'stop'
        else:
            self.__motor_command(finger, ACTIONS['stop'], 297)

    def open_fingers(self, velocity=None, force=True):
        """Opens all digits except thumb rotator at specified velocity.

        Parameters
        ----------
        velocity : int, optional
            Desired velocity.  Has to be in range (10,297). If not provided, the
            default velocity will be used.
        force : boolean, optional (default: True)
            If False and the finger status is ```opening``` or ```stalled
            open``` the command will not be sent.
        """
        velocity = self.def_vel if velocity is None else int(velocity)
        [self.open_finger(i, velocity=velocity, force=force) for i in range(
            1, N_DOF)]

    def open_all(self, velocity=None, force=True):
        """Opens all digits including thumb rotator at specified velocity.

        Parameters
        ----------
        velocity : int, optional
            Desired velocity.  Has to be in range (10,297). If not provided, the
            default velocity will be used.
        force : boolean, optional (default: True)
            If False and the finger status is ```opening``` or ```stalled
            open``` the command will not be sent.
        """
        velocity = self.def_vel if velocity is None else int(velocity)
        self.open_fingers(velocity=velocity, force=force)
        threading.Timer(0.5, self.open_finger, [6, velocity, force]).start()

    def close_fingers(self, velocity=None, force=True):
        """Closes all digits except thumb rotator at specified velocity.

        Parameters
        ----------
        velocity : int, optional
            Desired velocity.  Has to be in range (10,297). If not provided, the
            default velocity will be used.
        force : boolean, optional (default: True)
            If False and the finger status is ```closing``` or ```stalled
            close``` the command will not be sent.
        """
        velocity = self.def_vel if velocity is None else int(velocity)
        [self.close_finger(i, velocity=velocity, force=force) for i in range(
            1, N_DOF)]

    def close_all(self, velocity=None, force=True):
        """Closes all digits including thumb rotator at specified velocity.

        Parameters
        ----------
        velocity : int, optional
            Desired velocity.  Has to be in range (10,297). If not provided, the
            default velocity will be used.
        force : boolean, optional (default: True)
            If False and the finger status is ```closing``` or ```stalled
            close``` the command will not be sent.
        """
        velocity = self.def_vel if velocity is None else int(velocity)
        self.close_finger(6, velocity=velocity, force=force)
        threading.Timer(0.5, self.close_fingers, [velocity, force]).start()

    def stop_fingers(self, force=True):
        """Stops execution of movement for all digits except thumb rotator.

        Parameters
        ----------
        force : boolean, optional (default: True)
            If the finger status is ```stop``` the command will not be sent.
        """
        [self.stop_finger(i, force=force) for i in range(1, N_DOF)]

    def stop_all(self, force=True):
        """Stops execution of movement for all digits including thumb
        rotator.

        Parameters
        ----------
        force : boolean, optional (default: True)
            If the finger status is ```stop``` the command will not be sent.
        """
        [self.stop_finger(i, force=force) for i in range(1, N_DOF + 1)]

    def __create_message(self, action, velocity):
        """Creates a CAN message for a motor command."""
        velocity = format(velocity, '04x')
        msg = [0] * 4
        msg[0] = '00'  # Empty
        msg[1] = str(action)
        msg[2] = velocity[0:2]
        msg[3] = velocity[2:4]
        return msg

    def __read_messages(self):
        """Reads at least one time the queue looking for messages. If a
        message is found, looks again until queue is empty or an error occurs.
        """
        stsResult = 0
        while not (stsResult & PCAN_ERROR_QRCVEMPTY):
            can_msg = self.bus.Read(self.channel)
            if can_msg[0] == PCAN_ERROR_OK:
                self.__process_message(can_msg)
            stsResult = can_msg[0]

    def __process_message(self, can_msg):
        """Processes an incoming CAN message and updates finger_status and
        finger_current attributes.
        """
        finger_id = self.__can_to_finger_id(hex(can_msg[1].ID))
        self.finger_status[finger_id - 1] = STATUS[can_msg[1].DATA[1]]
        self.__is_moving = bool(len(set(self.finger_status) &
                                    {'opening', 'closing'}))
        current_hex = str(can_msg[1].DATA[2]) + str(can_msg[1].DATA[3])
        current_hex = str(int(hex(can_msg[1].DATA[2]), 16)) + str(int(hex(
            can_msg[1].DATA[3]), 16))
        # See p. 11 of robo-limb manual for conversion to Amps
        self.finger_current[finger_id - 1] = int(current_hex, 16) / 21.825

    def __motor_command(self, finger, action, velocity):
        """Issues a low-level finger command."""
        CANMsg = TPCANMsg()
        CANMsg.ID = self.__finger_to_can_id(finger)
        CANMsg.LEN = 4
        CANMsg.MSGTYPE = PCAN_MESSAGE_STANDARD
        msg = self.__create_message(action=action, velocity=velocity)
        for i in range(CANMsg.LEN):
            CANMsg.DATA[i] = int(msg[i], 16)
        self.bus.Write(self.channel, CANMsg)

    def __get_finger_id(self, finger):
        """Returns finger ID. Input can be either int or string."""
        return FINGERS[finger] if isinstance(finger, str) else int(finger)

    def __finger_to_can_id(self, finger):
        """Returns the CAN ID from a corresponding finger ID."""
        return int('0x10' + str(finger), 16)

    def __can_to_finger_id(self, id_string):
        """Returns the finger ID from a corresponding CAN ID."""
        return int(id_string[4])

    def __del__(self):
        self.stop()

    @property
    def is_moving(self):
        """Flag indicating whether at least one finger is moving."""
        return self.__is_moving
