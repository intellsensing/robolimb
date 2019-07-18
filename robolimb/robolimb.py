import threading

from can.interfaces.pcan.basic import (PCANBasic, PCAN_USBBUS1, PCAN_BAUD_1M,
                                       PCAN_TYPE_ISA, PCAN_ERROR_QRCVEMPTY,
                                       PCAN_ERROR_OK, TPCANMsg,
                                       PCAN_MESSAGE_STANDARD)

# Refer to robo-limb manual for definition of number codes below
N_DOF = 6
FINGERS = {
    'thumb': 1,
    'index': 2,
    'middle': 3,
    'ring': 4,
    'little': 5,
    'rotator': 6
}

ACTIONS = {
    'stop': 0,
    'close': 1,
    'open': 2
}

STATUS = {
    0: 'stop',
    1: 'closing',
    2: 'opening',
    3: 'stalled close',
    4: 'stalled open'
}

QUICK_GRIPS = {
    'normal': '00',
    'standard_precision_pinch_closed': '01',
    'standard_tripod_closed': '02',
    'thumb_park_continuous': '03',
    'lateral_grip': '05',
    'index_point': '06',
    'standard_precision_pinch_opened': '07',
    'thumb_precision_pinch_closed': '09',
    'thumb_precision_pinch_opened': '0A',
    'thumb_tripod_closed': '0B',
    'standard_tripod_opened': '0D',
    'thumb_tripod_opened': '0E',
    'cover': '18'
}


class RoboLimbCAN(object):
    """ Robo-limb control via CAN bus interface.

    Parameters
    ----------
    def_vel : int, optional (default: 297)
        Default velocity for finger control. Allowed range is (10,297).
    channel : pcan definition, optional (default: PCAN_USBBUS1)
        CAN communication channel.
    b_rate : pcan definition, optional (default: PCAN_BAUD_1M)
        CAN baud rate.
    hw_type : pcan definition, optional (default: PCAN_TYPE_ISA)
        CAN hardware type.
    io_port : hex,  (default: 0x3BC)
        CAN input-output port.
    interrupt : int, optional (default: 3)
        CAN interrupt handler.

    Attributes
    ----------
    finger_status_ : list
        Finger status.
    finger_current_ : list
        Finger currents.
    rotator_edge_ : bool
        ``True`` when rotator is fully palmar or lateral.
    is_moving_ : bool
        ``True`` if at least one digit is opening or closing.

    Notes
    -----
    There seems to be an issue with the current values provided by the hand.
    """

    def __init__(self,
                 def_vel=297,
                 channel=PCAN_USBBUS1,
                 b_rate=PCAN_BAUD_1M,
                 hw_type=PCAN_TYPE_ISA,
                 io_port=0x3BC,
                 interrupt=3):
        self.def_vel = def_vel
        self.channel = channel
        self.b_rate = b_rate
        self.hw_type = hw_type
        self.io_port = io_port
        self.interrupt = interrupt

        self.__finger_status = [None] * N_DOF
        self.__finger_current = [None] * N_DOF
        self.__rotator_edge = None

    def start(self):
        """Starts the CAN BUS connection."""
        self.bus = PCANBasic()
        self.bus.Initialize(
            Channel=self.channel,
            Btr0Btr1=self.b_rate,
            HwType=self.hw_type,
            IOPort=self.io_port,
            Interrupt=self.interrupt)

    def stop(self):
        """Stops reading incoming CAN messages and shuts down the
        connection."""
        self.bus.Uninitialize(Channel=self.channel)

    def open_finger(self, finger, velocity=None, force=True, update=True):
        """Opens digit at specified velocity.

        Parameters
        ----------
        finger : int or str
            Finger ID.
        velocity : int, optional
            Desired velocity.  Allowed range is (10,297). If not provided, the
            default velocity will be used.
        force : boolean, optional (default: True)
            If ``False`` and the finger status is ``opening`` or ``stalled
            open``, the command will not be sent.
        update : boolean, optional (default: True)
            When set to ``True``, the finger status will be queried. When set
            to ``False``, it is assumed that the finger status has been
            recently queried and the ``__finger_status`` attribute is up to
            date. When ``force`` is set to ``True``, this will be ignored.
        """
        velocity = self.def_vel if velocity is None else int(velocity)
        finger = self.__get_finger_id(finger)
        if force:
            send_command = True
        else:
            if update:
                self.__update_fingers()
            ok_status = ['opening', 'stalled open']
            if self.__finger_status[finger - 1] in ok_status:
                send_command = False
            else:
                send_command = True

        if send_command:
            self.__motor_command(finger, ACTIONS['open'], velocity)

    def close_finger(self, finger, velocity=None, force=True, update=True):
        """Closes digit at specified velocity.

        Parameters
        ----------
        finger : int or str
            Finger ID.
        velocity : int, optional
            Desired velocity.  Allowed range is (10,297). If not provided, the
            default velocity will be used.
        force : boolean, optional (default: True)
            If ``False`` and the finger status is ``closing`` or ``stalled
            close``, the command will not be sent.
        update : boolean, optional (default: True)
            When set to ``True``, the finger status will be queried. When set
            to ``False``, it is assumed that the finger status has been
            recently queried and the ``__finger_status`` attribute is up to
            date. When ``force`` is set to ``True``, this will be ignored.
        """
        velocity = self.def_vel if velocity is None else int(velocity)
        finger = self.__get_finger_id(finger)
        if force:
            send_command = True
        else:
            if update:
                self.__update_fingers()
            ok_status = ['closing', 'stalled close']
            if self.__finger_status[finger - 1] in ok_status:
                send_command = False
            else:
                send_command = True

        if send_command:
            self.__motor_command(finger, ACTIONS['close'], velocity)

    def stop_finger(self, finger, force=True, update=True):
        """Stops digit movement.

        Parameters
        ----------
        finger : int or str
            Finger ID.
        force : boolean, optional (default: True)
            If ``False`` and the finger status is ``stop`` or ``stalled
            open`` or ``stalled close``, the command will not be sent.
        update : boolean, optional (default: True)
            When set to ``True``, the finger status will be queried. When set
            to ``False``, it is assumed that the finger status has been
            recently queried and the ``__finger_status`` attribute is up to
            date. When ``force`` is set to ``True``, this will be ignored.
        """
        finger = self.__get_finger_id(finger)
        if force:
            send_command = True
        else:
            if update:
                self.__update_fingers()
            ok_status = ['stalled open', 'stalled close', 'stop']
            if self.__finger_status[finger - 1] in ok_status:
                send_command = False
            else:
                send_command = True

        if send_command:
            self.__motor_command(finger, ACTIONS['stop'], 297)

    def open_fingers(self, velocity=None, force=True, update=True):
        """Opens all digits except thumb rotator at specified velocity.

        Parameters
        ----------
        velocity : int, optional
            Desired velocity.  Allowed range is (10,297). If not provided, the
            default velocity will be used.
        force : boolean, optional (default: True)
            If ``False`` and the finger status is ``opening`` or ``stalled
            open``, the command will not be sent.
        update : boolean, optional (default: True)
            When set to ``True``, the finger status will be queried. When set
            to ``False``, it is assumed that the finger status has been
            recently queried and the ``__finger_status`` attribute is up to
            date. When ``force`` is set to ``True``, this will be ignored.

        Notes
        -----
        When ```update`` is ``True``, the finger status in queried once for all
        fingers before any finger specific commands are issued. The serial
        finger commands are then issued with ``update=False``.
        """
        velocity = self.def_vel if velocity is None else int(velocity)
        if not force and update:
            self.__update_fingers()

        [self.open_finger(i, velocity, force, False) for i in range(1, N_DOF)]

    def open_all(self, velocity=None, force=True, update=True):
        """Opens all digits including thumb rotator at specified velocity.

        Parameters
        ----------
        velocity : int, optional
            Desired velocity.  Allowed range is (10,297). If not provided, the
            default velocity will be used.
        force : boolean, optional (default: True)
            If ``False`` and the finger status is ``opening`` or ``stalled
            open``, the command will not be sent.
        update : boolean, optional (default: True)
            When set to ``True``, the finger status will be queried. When set
            to ``False``, it is assumed that the finger status has been
            recently queried and the ``__finger_status`` attribute is up to
            date. When ``force`` is set to ``True``, this will be ignored.

        Notes
        -----
        When ```update`` is ``True``, the finger status in queried once for all
        fingers before any finger specific commands are issued. The serial
        finger commands are then issued with ``update=False``.
        """
        velocity = self.def_vel if velocity is None else int(velocity)
        if not force and update:
            self.__update_fingers()

        self.open_fingers(velocity=velocity, force=force, update=False)
        threading.Timer(
            0.5,
            self.open_finger,
            [6, velocity, force, False]).start()

    def close_fingers(self, velocity=None, force=True, update=True):
        """Closes all digits except thumb rotator at specified velocity.

        Parameters
        ----------
        velocity : int, optional
            Desired velocity.  Allowed range is (10,297). If not provided, the
            default velocity will be used.
        force : boolean, optional (default: True)
            If ``False`` and the finger status is ``closing`` or ``stalled
            close``, the command will not be sent.
        update : boolean, optional (default: True)
            When set to ``True``, the finger status will be queried. When set
            to ``False``, it is assumed that the finger status has been
            recently queried and the ``__finger_status`` attribute is up to
            date. When ``force`` is set to ``True``, this will be ignored.

        Notes
        -----
        When ```update`` is ``True``, the finger status in queried once for all
        fingers before any finger specific commands are issued. The serial
        finger commands are then issued with ``update=False``.
        """
        velocity = self.def_vel if velocity is None else int(velocity)
        if not force and update:
            self.__update_fingers()

        [self.close_finger(i, velocity, force, False) for i in range(1, N_DOF)]

    def close_all(self, velocity=None, force=True, update=True):
        """Closes all digits including thumb rotator at specified velocity.

        Parameters
        ----------
        velocity : int, optional
            Desired velocity.  Allowed range is (10,297). If not provided, the
            default velocity will be used.
        force : boolean, optional (default: True)
            If ``False`` and the finger status is ``closing`` or ``stalled
            close``, the command will not be sent.
        update : boolean, optional (default: True)
            When set to ``True``, the finger status will be queried. When set
            to ``False``, it is assumed that the finger status has been
            recently queried and the ``__finger_status`` attribute is up to
            date. When ``force`` is set to ``True``, this will be ignored.

        Notes
        -----
        When ```update`` is ``True``, the finger status in queried once for all
        fingers before any finger specific commands are issued. The serial
        finger commands are then issued with ``update=False``.
        """
        velocity = self.def_vel if velocity is None else int(velocity)
        if not force and update:
            self.__update_fingers()

        self.close_finger(6, velocity=velocity, force=force, update=False)
        threading.Timer(
            0.5,
            self.close_fingers,
            [velocity, force, False]).start()

    def stop_fingers(self, force=True, update=True):
        """Stops movement for all digits except thumb rotator.

        Parameters
        ----------
        force : boolean, optional (default: True)
            If ``False`` and the finger status is ``stop`` or ``stalled
            open`` or ``stalled close``, the command will not be sent.
        update : boolean, optional (default: True)
            When set to ``True``, the finger status will be queried. When set
            to ``False``, it is assumed that the finger status has been
            recently queried and the ``__finger_status`` attribute is up to
            date. When ``force`` is set to ``True``, this will be ignored.

        Notes
        -----
        When ```update`` is ``True``, the finger status in queried once for all
        fingers before any finger specific commands are issued. The serial
        finger commands are then issued with ``update=False``.
        """
        if not force and update:
            self.__update_fingers()
        [self.stop_finger(i, force, False) for i in range(1, N_DOF)]

    def stop_all(self, force=True, update=True):
        """Stops movement for all digits including thumb rotator.

        Parameters
        ----------
        force : boolean, optional (default: True)
            If ``False`` and the finger status is ``stop`` or ``stalled
            open`` or ``stalled close``, the command will not be sent.
        update : boolean, optional (default: True)
            When set to ``True``, the finger status will be queried. When set
            to ``False``, it is assumed that the finger status has been
            recently queried and the ``__finger_status`` attribute is up to
            date. When ``force`` is set to ``True``, this will be ignored.

        Notes
        -----
        When ```update`` is ``True``, the finger status in queried once for all
        fingers before any finger specific commands are issued. The serial
        finger commands are then issued with ``update=False``.
        """
        if not force and update:
            self.__update_fingers()
        [self.stop_finger(i, force, False) for i in range(1, N_DOF + 1)]

    def quick_grip(self, grip):
        """Performs quick grip.

        Depending on the specified grip, some of the fingers will be locked and
        will not respond to open/close commands until the hand is set back to
        ``normal`` mode.

        Parameters
        ----------
        grip : type
            Description of parameter `grip`.
        """
        if grip not in QUICK_GRIPS.keys():
            raise ValueError("The specified grip is invalid.")

        id = int('0x301', 16)
        msg = ['0', '0', '0', QUICK_GRIPS[grip]]
        can_msg = self.__can_message(id, msg)

        self.bus.Write(self.channel, can_msg)

    def get_serial_number(self):
        """Queries the device serial number.

        Returns
        -------
        sn : str
            Device serial number.
        """
        id = int('0x402', 16)
        msg = ['0', '0', '0', '0']
        can_msg = self.__can_message(id, msg)

        # Reset queue such that first received message is the query response
        self.reset_bus()
        self.bus.Write(self.channel, can_msg)
        sn_msg = self.__read_messages(num_messages=1)[0]
        # See manual p.14 for message format
        letters = hex(sn_msg[1].DATA[0])[2:] + hex(sn_msg[1].DATA[1])[2:]
        numbers = hex(sn_msg[1].DATA[2])[2:] + hex(sn_msg[1].DATA[3])[2:]
        sn = bytearray.fromhex(letters).decode() + str(int(numbers, 16))
        return sn

    def reset_bus(self):
        """Resets the receive and transmit queues of the PCAN channel."""
        self.bus.Reset(self.channel)

    def __can_message(self, id, data):
        """Creates a CAN message from corresponding CAN ID and data.

        Parameters
        ----------
        message_id : int
            CAN message ID.

        message_data : list of str
            CAN message data. A list of strings of length 4 is expected.

        Returns
        -------
        can_msg : pcan definition
            CAN message.
        """
        can_msg = TPCANMsg()
        can_msg.ID = id
        can_msg.LEN = 4
        can_msg.MSGTYPE = PCAN_MESSAGE_STANDARD
        for i in range(can_msg.LEN):
            can_msg.DATA[i] = int(data[i], 16)

        return can_msg

    def __motor_command(self, finger, action, velocity):
        """Issues a low-level finger command.

        Parameters
        ----------
        finger : int or str
            Finger ID.
        action : str
            Finger action. One of ``['open', 'close', 'stop']``.
        velocity : int, optional
            Desired velocity.  Allowed range is (10,297). If not provided, the
            default velocity will be used.
        """
        id, data = self.__motor_message(finger, action, velocity)
        can_msg = self.__can_message(id, data)
        self.bus.Write(self.channel, can_msg)

    def __motor_message(self, finger, action, velocity):
        """Creates CAN message ID and data for a motor command.

        Parameters
        ----------
        finger : int or str
            Finger ID.
        action : str
            Finger action. One of ``['open', 'close', 'stop']``.
        velocity : int, optional
            Desired velocity.  Allowed range is (10,297). If not provided, the
            default velocity will be used.

        Returns
        -------
        id : int
            CAN message ID.
        data : list
            CAN message data.
        """
        id = self.__finger_to_can_id(finger)
        velocity = format(velocity, '04x')
        data = [0] * 4
        data[0] = '00'  # Empty
        data[1] = str(action)
        data[2] = velocity[0:2]
        data[3] = velocity[2:4]
        return id, data

    def __read_messages(self, num_messages=None):
        """Reads either a specified number of messages or all available
        messages from the queue.

        Parameters
        ----------
        num_messages : int, optional (default: None)
            Number of messages to read. If ``None``, read all messages unti
            queue is empty.

        Returns
        -------
        messages : list
            List of incoming CAN messages.

        Notes
        -----
        When the number of messages is specified, the method will block
        execution until the messages become available, i.e., there is no
        timeout implementation. If, for any reason, CAN messages do not arrive
        in the queue, the program may not exit the loop.
        """
        messages = []
        if num_messages:
            while len(messages) < num_messages:
                can_msg = self.bus.Read(self.channel)
                if can_msg[0] == PCAN_ERROR_OK:
                    messages.append(can_msg)
        else:
            res = 0
            while res != PCAN_ERROR_QRCVEMPTY:
                can_msg = self.bus.Read(self.channel)
                res = can_msg[0]
                if res == PCAN_ERROR_OK:
                    messages.append(can_msg)

        return messages

    def __process_feedback_message(self, can_msg):
        """Processes an incoming CAN feedback message.

        Parameters
        ----------
        can_msg : pcan definition
            CAN message.

        Returns
        -------
        finger_id : int
            Finger ID.
        status : str
            Finger status.
        thumb_edge : bool
            ``True when thumb rotator is fully palmar or lateral. For all other
            digits ``None`` will be returned.
        current : float
            Motor current (in Amps).
        """
        finger_id = self.__can_to_finger_id(hex(can_msg[1].ID))
        if finger_id == 6:
            thumb_edge = bool(int(hex(can_msg[1].DATA[0]), 16))
        else:
            thumb_edge = None
        status = STATUS[can_msg[1].DATA[1]]
        current_hex = '0x' + hex(can_msg[1].DATA[2])[2:] + \
            hex(can_msg[1].DATA[3])[2:]
        # See p. 11 of robo-limb manual for conversion to Amps
        current = int(current_hex, 16) / 21.825

        return (finger_id, status, thumb_edge, current)

    def __update_fingers(self):
        """Requests 6 CAN feedback messages and updates finger status and
        currents."""
        self.reset_bus()
        msgs = self.__read_messages(num_messages=6)
        for msg in msgs:
            result = self.__process_feedback_message(msg)
            f_id, f_status, thumb_edge, f_current = result
            self.__finger_status[f_id - 1] = f_status
            self.__finger_current[f_id - 1] = f_current
            if f_id == 6:
                self.__rotator_edge = thumb_edge

    def __get_quick_grip(self):
        """Queries quick grip.

        Returns
        -------
        grip : str
            Quick grip.
        """
        id = int('0x302', 16)
        msg = ['0', '0', '0', '0']
        can_msg = self.__can_message(id, msg)

        # Reset queue such that first received message is the query response
        self.reset_bus()
        self.bus.Write(self.channel, can_msg)
        grip_msg = self.__read_messages(num_messages=1)[0]
        # Grip codes have two digits, fill with zeros if needed
        code = hex(grip_msg[1].DATA[3])[2:].zfill(2)
        for grip_, code_ in QUICK_GRIPS.items():
            if code_ == code:
                grip = grip_

        return grip

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
        """Stops CAN bus connection upon destruction."""
        self.stop()

    @property
    def is_moving_(self):
        """Updates the digits status and returns `True` if at least one digit
        is opening or closing."""
        self.__update_fingers()
        return any(x in ['opening', 'closing'] for x in self.__finger_status)

    @property
    def finger_status_(self):
        """Updates the digits status and returns the result.

        Returns
        -------
        finger_status : list
                List of status with one element per digit.
        """
        self.__update_fingers()
        return self.__finger_status

    @property
    def rotator_edge_(self):
        """Updates the thumb rotator status and returns the result.

        Returns
        -------
        thumb_edge : bool
            `True` when thumb rotator is fully palmar or lateral.
        """
        self.__update_fingers()
        return self.__rotator_edge

    @property
    def finger_current_(self):
        """Updates the digits currents and returns the result.

        Returns
        -------
        finger_current : list
                List of currents with one element per digit.
        """
        self.__update_fingers()
        return self.__finger_current

    @property
    def quick_grip_(self):
        """Queries quick grip and returns the result.

        Returns
        -------
        grip : str
                Current quick grip.
        """
        return self.__get_quick_grip()
