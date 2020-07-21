[Keysight_E3631A]
    # Serial connection configuration.
    port = string
    baudrate = choice(300, 600, 1200, 2400, 4800, 9600)
    parity = choice('none', 'even', 'odd')
    data = choice(7, 8)
    timeout = integer(min=0)

    # Power supply voltage and current limitations.
    MIN_P6V_VOLTAGE = float(min=0, max=6)
    MAX_P6V_VOLTAGE = float(min=0, max=6)
    MIN_P25V_VOLTAGE = float(min=0, max=25)
    MAX_P25V_VOLTAGE = float(min=0, max=25)
    MIN_N25V_VOLTAGE = float(min=-25, max=0)
    MAX_N25V_VOLTAGE = float(min=-25, max=0)

    MIN_P6V_CURRENT = float(min=0, max=5)
    MAX_P6V_CURRENT = float(min=0, max=5)
    MIN_P25V_CURRENT = float(min=0, max=1)
    MAX_P25V_CURRENT = float(min=0, max=1)
    MIN_N25V_CURRENT = float(min=0, max=1)
    MAX_N25V_CURRENT = float(min=0, max=1)