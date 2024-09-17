import time
from pyModbusTCP.client import ModbusClient
import logging.config

logging.config.fileConfig('logging.config')
log = logging.getLogger('UPS_log')

IP_ADDRESS = '192.168.102.247'
PORT = 510
send_data = True


def Connection():
    c = ModbusClient(host=IP_ADDRESS, port=PORT, unit_id=1, auto_open=True)
    return c


def Reading_data():
    try:
        c = Connection()
        regs = c.read_coils(8192, 1)

        log.info(f"values from register is {regs}")
        c.close()
        if not regs:
            a = [0]
            return a
        else:
            return regs
    except Exception as err:
        log.error(f'Error PLC disconnected {err}')


def write_machine_off():
    try:
        c = Connection()
        regs = c.write_single_coil(8193, 1)
        regs2 = c.write_single_coil(8193, 0)
        log.info(f"we have done writing of register {regs}")
        log.info(f"we have done writing on register {regs2}")
        return regs, regs2
    except Exception as err:
        log.error(f'Error PLC disconnected {err}')



