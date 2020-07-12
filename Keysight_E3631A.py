
import copy
import math
import sys
import warnings

import serial

# These are constant values used for checking and establishing 
# power supply limits.
# These values are obtained from the factory manufactor. See 
# http://literature.cdn.keysight.com/litweb/pdf/E3631-90002.pdf#page=186&zoom=100,177,108
_FACTORY_MIN_P6V_VOLTAGE = 0.0
_FACTORY_MAX_P6V_VOLTAGE = 6.0
_FACTORY_MIN_P25V_VOLTAGE = 0.0
_FACTORY_MAX_P25V_VOLTAGE = 25.0
_FACTORY_MIN_N25V_VOLTAGE = -25.0
_FACTORY_MAX_N25V_VOLTAGE = 0.0

_FACTORY_MIN_P6V_CURRENT = 0.0
_FACTORY_MAX_P6V_CURRENT = 5.0
_FACTORY_MIN_P25V_CURRENT = 0.0
_FACTORY_MAX_P25V_CURRENT = 1.0
_FACTORY_MIN_N25V_CURRENT = 0.0
_FACTORY_MAX_N25V_CURRENT = 1.0
# These values are user created limitations to the output of the
# power supply. Default to the factory limitations.
USER_MIN_P6V_VOLTAGE = copy.deepcopy(_FACTORY_MIN_P6V_VOLTAGE)
USER_MAX_P6V_VOLTAGE = copy.deepcopy(_FACTORY_MAX_P6V_VOLTAGE)
USER_MIN_P25V_VOLTAGE = copy.deepcopy(_FACTORY_MIN_P25V_VOLTAGE)
USER_MAX_P25V_VOLTAGE = copy.deepcopy(_FACTORY_MAX_P25V_VOLTAGE)
USER_MIN_N25V_VOLTAGE = copy.deepcopy(_FACTORY_MIN_N25V_VOLTAGE)
USER_MAX_N25V_VOLTAGE = copy.deepcopy(_FACTORY_MAX_N25V_VOLTAGE)

USER_MIN_P6V_CURRENT = copy.deepcopy(_FACTORY_MIN_P6V_CURRENT)
USER_MAX_P6V_CURRENT = copy.deepcopy(_FACTORY_MAX_P6V_CURRENT)
USER_MIN_P25V_CURRENT = copy.deepcopy(_FACTORY_MIN_P25V_CURRENT)
USER_MAX_P25V_CURRENT = copy.deepcopy(_FACTORY_MAX_P25V_CURRENT)
USER_MIN_N25V_CURRENT = copy.deepcopy(_FACTORY_MIN_N25V_CURRENT)
USER_MAX_N25V_CURRENT = copy.deepcopy(_FACTORY_MAX_N25V_CURRENT)

# Default timeout value.
DEFAULT_TIMEOUT = 15
# The number of resolved digits kept by internal rounding
# by the power supply.
_SUPPLY_RESOLVED_DIGITS = 4

class Keysight_E3631A():
    """ This is a class that acts as a control for the 
    Keysight_E3631A power supply.
    """

    # Internal implimentation values.
    _P6V_voltage = float()
    _P25V_voltage = float()
    _N25V_voltage = float()
    _P6V_current = float()
    _P25V_current = float()
    _N25V_current = float()

    # Serial connection information.
    _serial_port = str()
    _serial_baudrate = int()
    _serial_parity = str()
    _serial_data = int()
    _serial_start = int()
    _serial_end = int()
    _serial_timeout = int()

    def __init__(self, port, baudrate=9600, parity=None, data=8,
                 timeout=DEFAULT_TIMEOUT, _sound=True):
        """ Creating the power supply instance. If successful, the 
        power supply will be put into remote mode automatically.
        """
        # Assign parity based on entry.
        parity = str(parity).lower() if (parity is not None) else 'none'
        if (parity == 'none'):
            parity = serial.PARITY_NONE
        elif (parity == 'even'):
            parity = serial.PARITY_EVEN
        elif (parity == 'odd'):
            parity = serial.PARITY_ODD
        else:
            # Parity can only be None, Even, or Odd for this 
            # instrument.
            raise ValueError("The parity must be either: "
                             "'none', 'even', or 'odd'.")

        # Assign the serial connection information.
        self._serial_port = str(port)
        self._serial_baudrate = int(baudrate)
        self._serial_parity = parity
        self._serial_data = int(data)
        self._serial_timeout = int(timeout)
        # These are set by Keysight hardware and are unchangeable.
        # See http://literature.cdn.keysight.com/litweb/pdf/E3631-90002.pdf#page=73&zoom=100,177,108
        self._serial_start = int(1)
        self._serial_end = int(2)

        # Load up the serial connection and send a test command.
        if ((len(self.version()) == 0) and 
            (len(self.send_scpi_command('*IDN?')) == 0)):
            # There was no responce to the system version command.
            # There does not seem to be a Keysight E3631A 
            # attached to this interface.
            warnings.warn("There is no responce from the port `{port}`. "
                          "The instrument may not be communicating back "
                          "with this class. Some functions may fail."
                          .format(port=self._serial_port),
                          RuntimeWarning, stacklevel=1)
        else:
            # Set the system into remote mode.
            __ = self.remote_mode()

        # Attempt the melody for confirmation and to also test 
        # out the timeout.
        if (_sound):
            # Beeping three times for confirmation of the class 
            # properly sending a command to the supply.
            __ = self.beep()
            __ = self.beep()
            __ = self.beep()
        else:
            # The user does not want any fun, or prefers the silence.
            pass
        # All done?
        return None

    # Sends a beep command.
    def beep(self):
        """ Sends a beep command to the power supply.
        """
        # The beep scpi command.
        beep_command = 'SYSTem:BEEPer:IMMediate'
        # Sending the beep command.
        responce = self.send_scpi_command(command=beep_command)
        # All done.
        return responce

    # SCPI command for the version.
    def version(self):
        """ This sends a command to fetch the current version of
        the SCPI protocol.
        """
        # Send the command.
        version_command = 'SYSTem:VERSion?'
        responce = self.send_scpi_command(command=version_command)
        # All done.
        return responce

    # This allows the power supply to be put into remote or local
    # mode. The local button still overrides.
    def remote_mode(self):
        """ This function sends a command to the power supply to 
        put it in remote mode. Remote mode means it is controlled by 
        this class. """
        # Send the remote mode command to the power supply.
        remote_command = 'SYSTem:REMote'
        responce = self.send_scpi_command(command=remote_command)
        # All done.
        return responce
    def local_mode(self):
        """ This function sends a command to the power supply to 
        put it in local mode. Local mode means it is controlled by 
        the front interface.
        """
        # Send the local mode command to the power supply.
        local_command = 'SYSTem:LOCal'
        responce = self.send_scpi_command(command=local_command)
        # All done.
        return responce
    # Aliases...
    local = local_mode
    remote = remote_mode

    # The implementation for the 6V output for the power supply.
    def get_P6V_voltage(self):
        """ This gets the voltage of the powersupply, it also 
        checks the variable value and the one obtained directly.
        """
        # It is always a good idea to double check against the
        # power supply itself.
        request_command = self._generate_apply_command(
            output='P6V', voltage=None, current=None, request=True)
        result = self.send_scpi_command(command=request_command)
        # The result contains both the voltage and the current split
        # by a comma.
        volt, __ = result.split(',')
        volt = volt.strip('"')
        supply_voltage = float(volt)
        # Double check that the two voltages are the same.
        assert_bool = math.isclose(supply_voltage, self._P6V_voltage)
        assert_message = ("The supply P6V voltage and the class voltage "
                          "are not the same. Assign a voltage via "
                          "the class before reading the voltage. "
                          "Keep the power supply in remote mode to "
                          "prevent this behavior. \n "
                          "Class: {cls_volt}  Power Supply: {ps_volt}"
                          .format(cls_volt=self._P6V_voltage,
                                  ps_volt=supply_voltage))
        assert assert_bool, assert_message
        # All good, as they are close, it does not matter which is 
        # returned.
        return supply_voltage
    def set_P6V_voltage(self, volt):
        """ Sets the voltage of the power supply. Checks exist to 
        ensure that the power supply range is not abnormal. 
        """
        # Ensure that the voltage value is not outside the 
        # power supply's manufacture's limit.
        if (_FACTORY_MIN_P6V_VOLTAGE <= volt <= _FACTORY_MAX_P6V_VOLTAGE):
            # The voltage is within the manufacture's limit.
            pass
        else:
            raise ValueError("The attempted voltage value is {volt}. This "
                             "is outside the factory specifications for the "
                             "P6V output: {min} <= V <= {max}."
                             .format(volt=volt, min=_FACTORY_MIN_P6V_VOLTAGE, 
                                     max=_FACTORY_MAX_P6V_VOLTAGE))
        # Ensure that the voltage value is not outside the user 
        # defined limits.
        if (USER_MIN_P6V_VOLTAGE <= volt <= USER_MAX_P6V_VOLTAGE):
            # The voltage is within the user's limit.
            pass
        else:
            raise ValueError("The attempted voltage value is {volt}. This "
                             "is outside the user limitations for the "
                             "P6V output: {min} <= V <= {max}."
                             .format(volt=volt, min=USER_MIN_P6V_VOLTAGE, 
                                     max=USER_MAX_P6V_VOLTAGE))
        # The power supply only supports a rounded voltage value to
        # the 3rd decimal point.
        volt = round(volt, _SUPPLY_RESOLVED_DIGITS)
        # The voltage passed the internal checks for safety. It can
        # be applied.
        self._P6V_voltage = volt
        # Send the command to the power supply.
        command = self._generate_apply_command(
            output='P6V', voltage=self._P6V_voltage, 
            current=self._P6V_current, request=False)
        __ = self.send_scpi_command(command=command)
        # All done.
        return None
    def del_P6V_voltage(self):
        """ This is the deletion method for this power supply's 
        voltage. Though, it should not be possible as it does not
        make sense to delete it.
        """
        # It does not make sense to delete the voltage.
        raise RuntimeError("You cannot delete the P6V voltage of "
                           "your power supply.")
        return None
    # The user interface of the voltage.
    P6V_voltage = property(get_P6V_voltage, set_P6V_voltage, 
                           del_P6V_voltage)
    def get_P6V_current(self):
        """ This gets the current of the powersupply, it also 
        checks the variable value and the one obtained directly.
        """
        # It is always a good idea to double check against the
        # power supply itself.
        request_command = self._generate_apply_command(
            output='P6V', voltage=None, current=None, request=True)
        result = self.send_scpi_command(command=request_command)
        # The result contains both the voltage and the current split
        # by a comma.
        __, curr = result.split(',')
        curr = curr.strip('"')
        supply_current = float(curr)
        # Double check that the two currents are the same.
        assert_bool = math.isclose(supply_current, self._P6V_current)
        assert_message = ("The supply P6V current and the class current "
                          "are not the same. Assign a current via "
                          "the class before reading the current. "
                          "Keep the power supply in remote mode to "
                          "prevent this behavior. \n "
                          "Class: {cls_curr}  Power Supply: {ps_curr}"
                          .format(cls_curr=self._P6V_current,
                                  ps_volt=supply_current))
        assert assert_bool, assert_message
        # All good, as they are close, it does not matter which is 
        # returned.
        return supply_current
    def set_P6V_current(self, curr):
        """ Sets the current of the power supply. Checks exist to 
        ensure that the power supply range is not abnormal. 
        """
        # Ensure that the voltage value is not outside the 
        # power supply's manufacture's limit.
        if (_FACTORY_MIN_P6V_CURRENT <= curr <= _FACTORY_MAX_P6V_CURRENT):
            # The voltage is within the manufacture's limit.
            pass
        else:
            raise ValueError("The attempted current value is {curr}. This "
                             "is outside the factory specifications for the "
                             "P6V output: {min} <= A <= {max}."
                             .format(curr=curr, min=_FACTORY_MIN_P6V_CURRENT, 
                                     max=_FACTORY_MAX_P6V_CURRENT))
        # Ensure that the current value is not outside the user 
        # defined limits.
        if (USER_MIN_P6V_CURRENT <= curr <= USER_MAX_P6V_CURRENT):
            # The current is within the user's limit.
            pass
        else:
            raise ValueError("The attempted current value is {curr}. This "
                             "is outside the user limitations for the "
                             "P6V output: {min} <= V <= {max}."
                             .format(curr=curr, min=USER_MIN_P6V_CURRENT, 
                                     max=USER_MAX_P6V_CURRENT))
        # The power supply only supports a rounded current value to
        # the 3rd decimal point.
        curr = round(curr, _SUPPLY_RESOLVED_DIGITS)
        # The current passed the internal checks for safety. It can
        # be applied.
        self._P6V_current = curr
        # Send the command to the power supply.
        command = self._generate_apply_command(
            output='P6V', voltage=self._P6V_voltage, 
            current=self._P6V_current, request=False)
        __ = self.send_scpi_command(command=command)
        # All done.
        return None
    def del_P6V_current(self):
        """ This is the deletion method for this power supply's 
        current. Though, it should not be possible as it does not
        make sense to delete it.
        """
        # It does not make sense to delete the current.
        raise RuntimeError("You cannot delete the P6V current of "
                           "your power supply.")
        return None
    # The user interface of the current.
    P6V_current = property(get_P6V_current, set_P6V_current, 
                           del_P6V_current)

    # The implementation for the +25V output for the power supply.
    def get_P25V_voltage(self):
        """ This gets the voltage of the powersupply, it also 
        checks the variable value and the one obtained directly.
        """
        # It is always a good idea to double check against the
        # power supply itself.
        request_command = self._generate_apply_command(
            output='P25V', voltage=None, current=None, request=True)
        result = self.send_scpi_command(command=request_command)
        # The result contains both the voltage and the current split
        # by a comma.
        volt, __ = result.split(',')
        volt = volt.strip('"')
        supply_voltage = float(volt)
        # Double check that the two voltages are the same.
        assert_bool = math.isclose(supply_voltage, self._P25V_voltage)
        assert_message = ("The supply P25V voltage and the class voltage "
                          "are not the same. Assign a voltage via "
                          "the class before reading the voltage. "
                          "Keep the power supply in remote mode to "
                          "prevent this behavior. \n "
                          "Class: {cls_volt}  Power Supply: {ps_volt}"
                          .format(cls_volt=self._P25V_voltage,
                                  ps_volt=supply_voltage))
        assert assert_bool, assert_message
        # All good, as they are close, it does not matter which is 
        # returned.
        return supply_voltage
    def set_P25V_voltage(self, volt):
        """ Sets the voltage of the power supply. Checks exist to 
        ensure that the power supply range is not abnormal.
        """
        # Ensure that the voltage value is not outside the 
        # power supply's manufacture's limit.
        if (_FACTORY_MIN_P25V_VOLTAGE <= volt <= _FACTORY_MAX_P25V_VOLTAGE):
            # The voltage is within the manufacture's limit.
            pass
        else:
            raise ValueError("The attempted voltage value is {volt}. This "
                             "is outside the factory specifications for the "
                             "P25V output: {min} <= V <= {max}."
                             .format(volt=volt, min=_FACTORY_MIN_P25V_VOLTAGE, 
                                     max=_FACTORY_MAX_P25V_VOLTAGE))
        # Ensure that the voltage value is not outside the user 
        # defined limits.
        if (USER_MIN_P25V_VOLTAGE <= volt <= USER_MAX_P25V_VOLTAGE):
            # The voltage is within the user's limit.
            pass
        else:
            raise ValueError("The attempted voltage value is {volt}. This "
                             "is outside the user limitations for the "
                             "P25V output: {min} <= V <= {max}."
                             .format(volt=volt, min=USER_MIN_P25V_VOLTAGE, 
                                     max=USER_MAX_P25V_VOLTAGE))
        # The power supply only supports a rounded voltage value to
        # the 3rd decimal point.
        volt = round(volt, _SUPPLY_RESOLVED_DIGITS)
        # The voltage passed the internal checks for safety. It can
        # be applied.
        self._P25V_voltage = volt
        # Send the command to the power supply.
        command = self._generate_apply_command(
            output='P25V', voltage=self._P25V_voltage, 
            current=self._P25V_current, request=False)
        __ = self.send_scpi_command(command=command)
        # All done.
        return None
    def del_P25V_voltage(self):
        """ This is the deletion method for this power supply's 
        voltage. Though, it should not be possible as it does not
        make sense to delete it.
        """
        # It does not make sense to delete the voltage.
        raise RuntimeError("You cannot delete the P25V voltage of "
                           "your power supply.")
        return None
    # The user interface of the voltage.
    P25V_voltage = property(get_P25V_voltage, set_P25V_voltage,
                            del_P25V_voltage)
    def get_P25V_current(self):
        """ This gets the current of the powersupply, it also 
        checks the variable value and the one obtained directly.
        """
        # It is always a good idea to double check against the
        # power supply itself.
        request_command = self._generate_apply_command(
            output='P25V', voltage=None, current=None, request=True)
        result = self.send_scpi_command(command=request_command)
        # The result contains both the voltage and the current split
        # by a comma.
        __, curr = result.split(',')
        curr = curr.strip('"')
        supply_current = float(curr)
        # Double check that the two currents are the same.
        assert_bool = math.isclose(supply_current, self._P25V_current)
        assert_message = ("The supply P25V current and the class current "
                          "are not the same. Assign a current via "
                          "the class before reading the current. "
                          "Keep the power supply in remote mode to "
                          "prevent this behavior. \n "
                          "Class: {cls_curr}  Power Supply: {ps_curr}"
                          .format(cls_curr=self._P25V_current,
                                  ps_volt=supply_current))
        assert assert_bool, assert_message
        # All good, as they are close, it does not matter which is 
        # returned.
        return supply_current
    def set_P25V_current(self, curr):
        """ Sets the current of the power supply. Checks exist to 
        ensure that the power supply range is not abnormal. 
        """
        # Ensure that the voltage value is not outside the 
        # power supply's manufacture's limit.
        if (_FACTORY_MIN_P25V_CURRENT <= curr <= _FACTORY_MAX_P25V_CURRENT):
            # The voltage is within the manufacture's limit.
            pass
        else:
            raise ValueError("The attempted current value is {curr}. This "
                             "is outside the factory specifications for the "
                             "P25V output: {min} <= A <= {max}."
                             .format(curr=curr, min=_FACTORY_MIN_P25V_CURRENT, 
                                     max=_FACTORY_MAX_P25V_CURRENT))
        # Ensure that the current value is not outside the user 
        # defined limits.
        if (USER_MIN_P25V_CURRENT <= curr <= USER_MAX_P25V_CURRENT):
            # The current is within the user's limit.
            pass
        else:
            raise ValueError("The attempted current value is {curr}. This "
                             "is outside the user limitations for the "
                             "P25V output: {min} <= V <= {max}."
                             .format(curr=curr, min=USER_MIN_P25V_CURRENT, 
                                     max=USER_MAX_P25V_CURRENT))
        # The power supply only supports a rounded current value to
        # the 3rd decimal point.
        curr = round(curr, _SUPPLY_RESOLVED_DIGITS)
        # The current passed the internal checks for safety. It can
        # be applied.
        self._P25V_current = curr
        # Send the command to the power supply.
        command = self._generate_apply_command(
            output='P25V', voltage=self._P25V_voltage, 
            current=self._P25V_current, request=False)
        __ = self.send_scpi_command(command=command)
        # All done.
        return None
    def del_P25V_current(self):
        """ This is the deletion method for this power supply's 
        current. Though, it should not be possible as it does not
        make sense to delete it.
        """
        # It does not make sense to delete the current.
        raise RuntimeError("You cannot delete the P25V current of "
                           "your power supply.")
        return None
    # The user interface of the current.
    P25V_current = property(get_P25V_current, set_P25V_current, 
                            del_P25V_current)

    # The implementation for the -25V output for the power supply.
    def get_N25V_voltage(self):
        """ This gets the voltage of the powersupply, it also 
        checks the variable value and the one obtained directly.
        """
        # It is always a good idea to double check against the
        # power supply itself.
        request_command = self._generate_apply_command(
            output='N25V', voltage=None, current=None, request=True)
        result = self.send_scpi_command(command=request_command)
        # The result contains both the voltage and the current split
        # by a comma.
        volt, __ = result.split(',')
        volt = volt.strip('"')
        supply_voltage = float(volt)
        # Double check that the two voltages are the same.
        assert_bool = math.isclose(supply_voltage, self._N25V_voltage)
        assert_message = ("The supply N25V voltage and the class voltage "
                          "are not the same. Assign a voltage via "
                          "the class before reading the voltage. "
                          "Keep the power supply in remote mode to "
                          "prevent this behavior. \n "
                          "Class: {cls_volt}  Power Supply: {ps_volt}"
                          .format(cls_volt=self._N25V_voltage,
                                  ps_volt=supply_voltage))
        assert assert_bool, assert_message
        # All good, as they are close, it does not matter which is 
        # returned.
        return supply_voltage
    def set_N25V_voltage(self, volt):
        """ Sets the voltage of the power supply. Checks exist to 
        ensure that the power supply range is not abnormal.
        """
        # Ensure that the voltage value is not outside the 
        # power supply's manufacture's limit.
        if (_FACTORY_MAX_N25V_VOLTAGE <= volt <= _FACTORY_MAX_N25V_VOLTAGE):
            # The voltage is within the manufacture's limit.
            pass
        else:
            raise ValueError("The attempted voltage value is {volt}. This "
                             "is outside the factory specifications for the "
                             "N25V output: {min} <= V <= {max}."
                             .format(volt=volt, min=_FACTORY_MAX_N25V_VOLTAGE, 
                                     max=_FACTORY_MAX_N25V_VOLTAGE))
        # Ensure that the voltage value is not outside the user 
        # defined limits.
        if (USER_MAX_N25V_VOLTAGE <= volt <= USER_MAX_N25V_VOLTAGE):
            # The voltage is within the users's limit.
            pass
        else:
            raise ValueError("The attempted voltage value is {volt}. This "
                             "is outside the user limitations for the "
                             "N25V output: {min} <= V <= {max}."
                             .format(volt=volt, min=USER_MAX_N25V_VOLTAGE, 
                                     max=USER_MAX_N25V_VOLTAGE))
        # The power supply only supports a rounded voltage value to
        # the 3rd decimal point.
        volt = round(volt, _SUPPLY_RESOLVED_DIGITS)
        # The voltage passed the internal checks for safety. It can
        # be applied.
        self._N25V_voltage = volt
        # Send the command to the power supply.
        command = self._generate_apply_command(
            output='N25V', voltage=self._N25V_voltage, 
            current=self._N25V_current, request=False)
        __ = self.send_scpi_command(command=command)
        # All done.
        return None
    def del_N25V_voltage(self):
        """ This is the deletion method for this power supply's 
        voltage. Though, it should not be possible as it does not
        make sense to delete it.
        """
        # It does not make sense to delete the voltage.
        raise RuntimeError("You cannot delete the N25V voltage of "
                           "your power supply.")
        return None
    # The user interface of the voltage.
    N25V_voltage = property(get_N25V_voltage, set_N25V_voltage, 
                            del_N25V_voltage)
    def get_N25V_current(self):
        """ This gets the current of the powersupply, it also 
        checks the variable value and the one obtained directly.
        """
        # It is always a good idea to double check against the
        # power supply itself.
        request_command = self._generate_apply_command(
            output='N25V', voltage=None, current=None, request=True)
        result = self.send_scpi_command(command=request_command)
        # The result contains both the voltage and the current split
        # by a comma.
        __, curr = result.split(',')
        curr = curr.strip('"')
        supply_current = float(curr)
        # Double check that the two currents are the same.
        assert_bool = math.isclose(supply_current, self._N25V_current)
        assert_message = ("The supply N25V current and the class current "
                          "are not the same. Assign a current via "
                          "the class before reading the current. "
                          "Keep the power supply in remote mode to "
                          "prevent this behavior. \n "
                          "Class: {cls_curr}  Power Supply: {ps_curr}"
                          .format(cls_curr=self._N25V_current,
                                  ps_volt=supply_current))
        assert assert_bool, assert_message
        # All good, as they are close, it does not matter which is 
        # returned.
        return supply_current
    def set_N25V_current(self, curr):
        """ Sets the current of the power supply. Checks exist to 
        ensure that the power supply range is not abnormal. 
        """
        # Ensure that the voltage value is not outside the 
        # power supply's manufacture's limit.
        if (_FACTORY_MIN_N25V_CURRENT <= curr <= _FACTORY_MAX_N25V_CURRENT):
            # The voltage is within the manufacture's limit.
            pass
        else:
            raise ValueError("The attempted current value is {curr}. This "
                             "is outside the factory specifications for the "
                             "N25V output: {min} <= A <= {max}."
                             .format(curr=curr, min=_FACTORY_MIN_N25V_CURRENT, 
                                     max=_FACTORY_MAX_N25V_CURRENT))
        # Ensure that the current value is not outside the user 
        # defined limits.
        if (USER_MIN_N25V_CURRENT <= curr <= USER_MAX_N25V_CURRENT):
            # The current is within the user's limit.
            pass
        else:
            raise ValueError("The attempted current value is {curr}. This "
                             "is outside the user limitations for the "
                             "N25V output: {min} <= V <= {max}."
                             .format(curr=curr, min=USER_MIN_N25V_CURRENT, 
                                     max=USER_MAX_N25V_CURRENT))
        # The power supply only supports a rounded current value to
        # the 3rd decimal point.
        curr = round(curr, _SUPPLY_RESOLVED_DIGITS)
        # The current passed the internal checks for safety. It can
        # be applied.
        self._N25V_current = curr
        # Send the command to the power supply.
        command = self._generate_apply_command(
            output='N25V', voltage=self._N25V_voltage, 
            current=self._N25V_current, request=False)
        __ = self.send_scpi_command(command=command)
        # All done.
        return None
    def del_N25V_current(self):
        """ This is the deletion method for this power supply's 
        current. Though, it should not be possible as it does not
        make sense to delete it.
        """
        # It does not make sense to delete the current.
        raise RuntimeError("You cannot delete the N25V current of "
                           "your power supply.")
        return None
    # The user interface of the current.
    N25V_current = property(get_N25V_current, set_N25V_current, 
                            del_N25V_current)

    # This command fetches which instrument output is selected.
    def selected_output(self):
        """ This function sends a command to the instrument to
        see what is the current specified active output.
        """
        # The command to get the current selected output.
        output_select_command = 'INSTrument:SELect?'
        responce = self.send_scpi_command(command=output_select_command)
        # All done.
        return responce

    # These functions handle the command interface of the serial
    # connection.
    def send_scpi_command(self, command):
        """ This function is a wrapper around sending a scpi command
        to the power supply. It performs internal checks to ensure 
        that the command send it proper. However, there are no
        checks here on the reasonableness of the command.

        The newline characters are automatically added to the 
        command sent and removed from the responce returned. Treat
        the input and output as normal SCPI ASCII strings.
        """
        # The command must be suffixed with a new line for the 
        # power supply to properly recognize it.
        command = ''.join([command, '\n'])

        # The most cross-platform solution is to just use the
        # default bytestring. Windows does not like simple strings.
        byte_command = bytearray(command, sys.getdefaultencoding())
        # Send the command and read back the responce.
        raw_responce = self._send_raw_scpi_command(bytestring=byte_command)
        responce = str(raw_responce.decode())
        # The responce usually has the endline, removing it.
        suffix = '\r\n'
        if responce.endswith(suffix):
            responce = responce[:-len(suffix)]
        else:
            responce = responce

        # All done.
        return responce
    def _send_raw_scpi_command(self, bytestring):
        """ This function sends a remote command to the power supply
        for it to execute. No internet checks are done. This is 
        mostly a wrapper for the serial package. Moreover, the
        input and outputs are not formatted and are instead raw
        for and from serial.
        """
        # Load the serial connection information.
        port = self._serial_port
        baudrate = self._serial_baudrate
        parity = self._serial_parity
        data = self._serial_data
        start_bits = self._serial_start
        end_bits = self._serial_end
        timeout = self._serial_timeout

        # Load up the serial connection.
        with serial.Serial(
            port=port, baudrate=baudrate, bytesize=data,
            parity=parity, stopbits=end_bits, timeout=timeout) as ser:
            # Sending the command.
            ser.write(bytestring)
            # Read the responce, if any.
            if (timeout is None):
                # There is no timeout, the script will hang forever
                # if nothing is received. Using the default timeout
                # value.
                _old_timeout = copy.deepcopy(self._serial_timeout)
                ser.timeout = DEFAULT_TIMEOUT
                # Read the responce.
                responce = ser.readline()
                # Restore the old timeout value.
                ser.timeout = _old_timeout
            else:
                # There is a timeout, so just read the line.
                responce = ser.readline()

        # All done. Output the responce.
        return responce


        # The apply command is the easiest way to set voltages and 
    # Aliases.
    command = send = write = send_scpi_command
    
    # Internal consistency function for the voltage property 
    # interfaces.
    def _generate_apply_command(self, output, voltage, current,
                                request=False):
        """ This is just a wrapper function to spit out a string
        that is a APPLy valid command for the function used. This 
        is only used for the variable interfaces and should not 
        be used otherwise.
        """
        ## Type check and validate.
        # Instrument type checking.
        output = str(output).upper()
        if (output in ('P6V','P25V','N25V')):
            # A valid instrument type.
            pass
        else:
            raise ValueError("The output specified is `{out}`, it must be "
                             "one the the following: 'P6V', 'P25V', 'N25V'"
                             .format(out=output))
        # The voltages and currents should be string represented. 
        # Also, if the parameter 'DEF', 'MIN', or 'MAX' is used, that
        # should be passed through instead.
        # Voltage
        if ((str(voltage).upper() in ('','DEF','MIN','MAX')) or 
            (voltage is None)):
            # Begin to convert.
            voltage = '' if (voltage is None) else voltage
            voltage_str = str(voltage).upper()
        else:
            voltage_str = '{:6f}'.format(float(voltage))
        # Current
        if ((str(current).upper() in ('','DEF','MIN','MAX')) or 
            (current is None)):
            # Begin to convert.
            current = '' if (current is None) else current
            current_str = str(current).upper()
        else:
            current_str = '{:6f}'.format(float(current))

        # Compile the command itself. If the user wants a request 
        # form, then compile that instead.
        if (request):
            # This is a request apply command.
            apply_command = ('APPLy? {out}'.format(out=output))
        else:
            apply_command = ('APPLy {out},{volt},{curr}'
                             .format(out=output, 
                                     volt=voltage_str, curr=current_str))
        # All done.
        return apply_command
