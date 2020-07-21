# Keysight-E3631A-Python
This repository contains a class which acts as a Python interface for the remote operation of a Keysight E3631A Triple Output DC Power Supply. [The manual for the device](https://github.com/psmd-iberutaru/Keysight-E3631A-Python/blob/master/Keysight_E3631A_Factory_Manual.pdf).

Allegiant initially developed this power supply, the ownership was transferred to Keysight.

## Introduction
The Python class developed here acts as a Python interface with the Keysight E3631A's remote operations. Only RS-232 DE-9 interface connectors are supported by this class. This class is a wrapper around [pyserial](https://pyserial.readthedocs.io/en/latest/index.html) and the SCPI command interface over RS-232. 

All of the commands are Python wrappers to try and expose the serial and SCPI interface into more native Python constructs.

### Setup
There is no *installation* per say. The entire class is self-contained in one file: [Keysight_E3831A.py](https://github.com/psmd-iberutaru/Keysight-E3631A-Python/blob/master/Keysight_E3631A.py) However, you need to install the `pyserial` package. You can generally do this by: `pip install pyserial`

Moreover, it is suggested that this package be used with Python 3 (but, it still works with Python 2 with one caveat). 
This package and its class is best put in the same directory as whichever project needs it compared to installing it in your Python path.

## Usage
To use this class, it is pretty simple. First, we will import it as we would any other local package. There are two ways:
```python
from Keysight_E3631A import Keysight_E3631A
```

...or...
```python
import Keysight_E3631A as keysight
```
The first directly allows interface into the class itself. However, it does not easily allow for the setting of user defined limits (see **Defined limits**).

Nevertheless, which ever method is used, the class `Keysight_E3631A` is what is important. It is also the same name as the file, so, try not to get confused.

### Create class and connect
You need to know which port your power supply is connected to. You can get a list of available serial ports with: `python  -m  serial.tools.list_ports`
Once you have determined which port your instrument is connected to, you can create your class. 
```python
import Keysight_E3631A as keysight
power_supply = keysight.Keysight_E3631A(port='port_name', 
	baudrate=9600, parity=None, data=8, timeout=1, _sound=True)
```

You can also create a class using a configuration dictionary containing the terms key-value described below. The proper way to create a class using a configuration dictionary is described below: (This also allows you to use a configuration file through [configparser](https://docs.python.org/3/library/configparser.html) or similar packages.)
```python
import Keysight_E3631A as keysight

serial_dict = {'port':'port_name', 'baudrate':9600, 
	       'parity':'none', 'data':8, 'timeout':2}
limit_dict = {'MIN_P6V_VOLTAGE':0.0,
              'MAX_P6V_VOLTAGE':6.0,
              'MIN_P25V_VOLTAGE':0.0,
              'MAX_P25V_VOLTAGE':25.0,
              'MIN_N25V_VOLTAGE':-25.0,
              'MAX_N25V_VOLTAGE':0.0}
# Combine the two.
config_dict = {**serial_dict, **limit_dict}


power_supply = keysight.Keysight_E3631A.load_configuration(config_dict, _flat=False)
```

Here, the terms mean:

* **port** : the name of the port connection, generally a string
* **baudrate** : the baudrate that the power supply is set to (the Keysight E3631A default is 9600)
* **parity** : the parity bit setting that the power supply is set to (the Keysight E3631A default is None)
* **data** : the data bit setting that the power supply is set to (the Keysight E3631A default is 8)
* **timeout** : the timeout time, in seconds, that the class will wait for the power supply to send back a response (if none is put, it defaults to 15 seconds or `keysight.DEFAULT_TIMEOUT`)
* **_sound** : a *hidden* parameter, the power supply will beep in confirmation when the class is created; you can set this to False to disable this functionality

Once the power supply is initiated, it will normally send a version and identify command to the power supply and wait for a response (as dictated by the timeout input). If it does not get a response, then it may not be able to connect to the power supply. It will warn you if the class instance does not get a non-empty responce. It will also attempt to send beep commands (unless `_sound` is disabled). If you do not hear the beeps, check that the power supply and the class settings are the same. For more information on setting the RS-232 parameters on your power supply, see the [manual (page 73)](https://github.com/psmd-iberutaru/Keysight-E3631A-Python/blob/master/Keysight_E3631A_Factory_Manual.pdf).

On some Linux machines, there may be insignificant permissions for this class to communicate with the port interface. This can generally be solved by executing the following in the Linux terminal to change the permissions:
```bash
sudo chmod 777 path/to/port
```

### Programing
The power supply has three outputs, they are named by the power supply as `P6V`, `P25V`, and `N25V`. They stand for +6 volts, +25 volts, and -25 volts, the general range of the three different outputs. See the [manual (page 186)](https://github.com/psmd-iberutaru/Keysight-E3631A-Python/blob/master/Keysight_E3631A_Factory_Manual.pdf) for more information. 

The `Keysight_E3631A()`  class can interface with all three outputs using the class attributes:

 - **+6V**
	 - Voltage:`Keysight_E3631A.P6V_voltage`
	 - Current: `Keysight_E3631A.P6V_current`
 - **+25V**
	 - Voltage:`Keysight_E3631A.P25V_voltage`
	 - Current: `Keysight_E3631A.P25V_current`
-  **+6V**
	 - Voltage:`Keysight_E3631A.N25V_voltage`
	 - Current: `Keysight_E3631A.N25V_current`

These attributes control the power supply's current and voltages for each of the three outputs. They interface like normal python attributes, setting one of the attributes with a value assigns the voltage to the power supply.

For example, to set the power supply's +6V output to have a voltage of 3 volts and a current of 1.42 amperes, the following code snippet should work. (The port settings are assumed to be defaults/fillers, please change it to what is required.)
```python
# Import the package into whichever script is needed.
import Keysight_E3631A as keysight

# Create a power supply instance, it should automatically 
# connect and test the connection with a few commands 
# and beeps.
power_supply = keysight.Keysight_E3631A(port='port_name', 
	baudrate=9600, parity=None, data=8, timeout=1, _sound=True)

# Set the voltage of the +6V/P6V output to 3 volts.
power_supply.P6V_voltage = 3
print(power_supply.P6V_voltage) # Should print 3

# Set the current of the +6V/P6V output to 1.42 amperes.
power_supply.P6V_current = 1.42
print(power_supply.P6V_current) # Should print 1.42
```

From there, check the +6V output of your power supply, you should be able to see that the voltage and current are what is programed. You may also see it programed on the display of your power supply. The above code snippet extrapolates to `Keysight_E3631A.P25V_*` and `Keysight_E3631A.N25V_*` for +25V and -25v outputs.

*(If you are using Python 2, the interface used above is not valid as the property() function is not avaliable. Please use the getter/setters `Keysight_E3631A.get_P6V_voltage`, `Keysight_E3631A.set_P6V_voltage`, and `Keysight_E3631A.del_P6V_voltage` to interface with the power supply. These getters/setters extend to the currents (i.e. `Keysight_E3631A.get_P6V_current` etc) and to the other two outputs (i.e. `Keysight_E3631A.get_N25V_voltage` and `Keysight_E3631A.get_P25V_current`). This is the caveat.)*

#### Custom SCPI commands
You can also send any general SCPI command to the power supply using `Keysight_E3631A.send_scpi_command(command='command')` (these aliases are available: `command()`, `send()`, and `write()`). This command sends the inputted SCPI command to the power supply and will also read the response. If the SCPI command is not a valid command, the power supply insturment itself (and not the class instance)  will not accept it and will throw an error. (You can use `Keysight_E3631A.error()` to fetch the most recent error or use `Keysight_E3631A.clear()` to clear the entire event register, including errors.)

The usage of the script is highlighted in the following example. This example tells the power supply to beep. (The code below is very similar to how the function `Keysight_E3631A.beep()` is implemented.)
```python
# Import the package into whichever script is needed.
import Keysight_E3631A as keysight

# Create a power supply instance, it should automatically 
# connect and test the connection with a few commands 
# and beeps.
power_supply = keysight.Keysight_E3631A(port='port_name', 
	baudrate=9600, parity=None, data=8, timeout=1, _sound=True)

# The beep scpi command.
beep_command = 'SYSTem:BEEPer:IMMediate'

# Sending the beep command, we also capture the responce 
# from the power supply, here is an empty string. 
# The power supply should beep once you ran this instruction.
responce = self.send_scpi_command(command=beep_command)
```

For a more exhaustive list of available SCPI commands that can be sent to the power supply, see the [manual (page 83-124)](https://github.com/psmd-iberutaru/Keysight-E3631A-Python/blob/master/Keysight_E3631A_Factory_Manual.pdf). (Pages 125-130 serves as a brief introduction to SCPI syntax used in the manual and the commands themselves; pages 131-135 contains a plain list of all available commands without usage information.)

### Defined limits
The power supply has defined factory specifications, this Python package also allows the user to set their own limitations to further restrict the allowed voltages and current. Attempting to set a voltage or current level outside the limitations will raise a `ValueError`. 

These limits are only used for sending a voltage or current through the `power_supply.* = x` interface.

*(Please note that these limitations are not enforced when sending manual commands. It is assumed that sending manual SCPI commands are usually hardcoded so deference should be given to the user.)*

#### Factory limits
The factory specifications of the power supply contain these limitations (see [the manual (page 186)](https://github.com/psmd-iberutaru/Keysight-E3631A-Python/blob/master/Keysight_E3631A_Factory_Manual.pdf) for more information). 

 - **+6V output**
	 - Voltage: 0.0 V ≤ x ≤ +6.0 V
	 - Current: 0.0 A ≤ x ≤ +5.0 A 
 - **+25V output**
	 - Voltage: 0.0 V ≤ x ≤ +25.0 V
	 - Current: 0.0 A ≤ x ≤ +1.0 A 
 - **-25V output**
	 - Voltage: -25.0 V ≤ x ≤ +0.0 V
	 - Current: 0.0 A ≤ x ≤ +1.0 A 

These factory limits are semi-hard coded in the Python file and cannot be changed conventionally. We do not suggest changing these values. To assign your own limitations, use **User limits** or **Instance limits**.

#### User limits
Like the factory specification limits, user limits allow the user to constrain the entry of values such that they do not exceed a predetermined range. User limits default to the factory limits when they are not specified otherwise.

User limits are present in the package itself as Python convention  constant values. They are (here the values are the factory defaults):
```python
import Keysight_E3631A as keysight

# P6V user limits:
keysight.USER_MIN_P6V_VOLTAGE = 0.0
keysight.USER_MAX_P6V_VOLTAGE = 6.0
keysight.USER_MIN_P6V_CURRENT = 0.0
keysight.USER_MAX_P6V_CURRENT = 5.0
# P25V user limits:
keysight.USER_MIN_P25V_VOLTAGE = 0.0
keysight.USER_MAX_P25V_VOLTAGE = 25.0
keysight.USER_MIN_P25V_CURRENT = 0.0
keysight.USER_MAX_P25V_CURRENT = 1.0
# N25V user limits:
keysight.USER_MIN_N25V_VOLTAGE = -25.0
keysight.USER_MAX_N25V_VOLTAGE = 0.0
keysight.USER_MIN_N25V_CURRENT = 0.0
keysight.USER_MAX_N25V_CURRENT = 1.0
```

You can change any of these values like you would any attribute value: (The example below is changing the P6V output user maximum voltage to 4 volts.)
```python
import Keysight_E3631A as keysight
# Changing the user limit to 4 volts.
keysight.USER_MAX_P6V_VOLTAGE = 4.0
```

Please note that these limitations are applied across the board for all power supply instances within the current Python session. If you desire to limit a single power supply instance, use **Instance limits**

#### Instance limits
Like user limits, instance limits add another layer of limitation to the allowed voltage and current values that the power supply can be set to. They also default to the factory limits if there are no other predefined limit. However, unlike user limits, they only apply to a given power supply instance. 

The instance limits are found within a power supply instance, namely: (Again, the values here are just the factory defaults used if the user does not specify a instance limit.)
```python
import Keysight_E3631A as keysight

# Create a power supply instance.
power_supply = keysight.Keysight_E3631A(port='port_name', 
	baudrate=9600, parity=None, data=8, timeout=1, _sound=True)

# P6V instance limits:
power_supply.MIN_P6V_VOLTAGE = 0.0
power_supply.MAX_P6V_VOLTAGE = 6.0
power_supply.MIN_P6V_CURRENT = 0.0
power_supply.MAX_P6V_CURRENT = 5.0
# P25V instance limits:
power_supply.MIN_P25V_VOLTAGE = 0.0
power_supply.MAX_P25V_VOLTAGE = 25.0
power_supply.MIN_P25V_CURRENT = 0.0
power_supply.MAX_P25V_CURRENT = 1.0
# N25V instance limits:
power_supply.MIN_N25V_VOLTAGE = -25.0
power_supply.MAX_N25V_VOLTAGE = 0.0
power_supply.MIN_N25V_CURRENT = 0.0
power_supply.MAX_N25V_CURRENT = 1.0
```

You can change any of these values like you would any attribute value: (The example below is changing the P6V output instance maximum voltage to 2.3 volts.)
```python
import Keysight_E3631A as keysight

# Create a power supply instance.
power_supply = keysight.Keysight_E3631A(port='port_name', 
	baudrate=9600, parity=None, data=8, timeout=1, _sound=True)

# Changing the instance limit to 2.3 volts.
power_supply.MAX_P6V_VOLTAGE = 2.3
```

---
*(Please note, if two or more power supply instances are used to control the same power supply connected to the same port, only their own instance limitations will be applied to themselves. As such, the following is possible:*
```python
import Keysight_E3631A as keysight
# Creating the power supply instances.
power_supply_1 = keysight.Keysight_E3631A(port='same_port_name', 
	baudrate=9600, parity=None, data=8, timeout=1, _sound=True)
power_supply_2 = keysight.Keysight_E3631A(port='same_port_name', 
	baudrate=9600, parity=None, data=8, timeout=1, _sound=True)

# Changing power_supply_1 instance limit to 3 volts.
power_supply_1.MAX_P6V_VOLTAGE = 3
# power_supply_2 should still have the factory default values.
print(power_supply_2.MAX_P6V_VOLTAGE == 6.0)
#print(keysight._FACTORY_MAX_P6V_VOLTAGE == 6.0)

# Change the power supply's voltage to 2 volts via power_supply_1.
power_supply_1.P6V_voltage = 2.0
# Change the power supply's voltage to 5 volts via power_supply_2.
power_supply_2.P6V_voltage = 4.0
# This exceeds the limit from power_supply_1, but power_supply_2 
# does not know they are the same insturment; it is allowed as
# nothing from power_supply_2 prohibits 4.0 volts and both
# power_supply_1 and power_supply 2 are oblivious to each other.

# Check the power supply's voltage from power_supply_1.
print(power_supply_1.P6V_voltage)
# This will raise an AssertionError. As power_supply_1 is expecting 
# the voltage to be 2.0 volts, but the real insturment returns 4.0 
# volts because it was changed by power_supply_2. These two values 
# do not match, the instance does not know which value is the 
# expected truth, it must stop. The code will not assume anything.
```
*We suggest that you do not try and use more than one `Keysight_E3631A()` instance per port per power supply. We highly advise againsrt abusing this functionality.)*

## Documentation
All of the documentation for this entire package is both in this [README.md](https://github.com/psmd-iberutaru/Keysight-E3631A-Python/blob/master/README.md) and the [`Keysight_E3631A.py` Python package file](https://github.com/psmd-iberutaru/Keysight-E3631A-Python/blob/master/Keysight_E3631A.py) docstrings. 

### Contributing
Feel free to open up an issue or a pull request if you have any additions to this package for others.

#### License
This package and documentation is licensed under the [MIT License](https://github.com/psmd-iberutaru/Keysight-E3631A-Python/blob/master/LICENSE)   for all intents and purposes. 
