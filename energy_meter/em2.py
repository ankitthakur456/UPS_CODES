import os
import time
import minimalmodbus
import serial
import serial.tools.list_ports
import logging.config

logging.config.fileConfig('logging.config')
log = logging.getLogger('UPS_log')


# region Rotating Logs
dirname = os.path.dirname(os.path.abspath(__file__))


# reion Global Variables
GL_SEND_DATA = True
SAMPLE_RATE = 5


# endregion
def combine_cdab(value1, value2):
    # Combine the two values into a 32-bit integer in CDAB order
    # value1 = CD part (higher 16 bits), value2 = AB part (lower 16 bits)
    combined = (value1 << 16) | value2
    return combined

# region Modbus functions
def initiate(slaveId):
    com_port = None
    for i in range(5):
        try:
            ports = serial.tools.list_ports.comports()
            usb_ports = [p.device for p in ports if "USB" in p.description]
            log.info(usb_ports)
            com_port = usb_ports[1]
            break
        except Exception as e:
            log.info(f"[-] Error Can't Open Port {e}")
            com_port = None
            time.sleep(1)

    i = int(slaveId)
    instrument = minimalmodbus.Instrument(com_port, i)
    instrument.serial.baudrate = 19200
    instrument.serial.bytesize = 8
    instrument.serial.parity = serial.PARITY_EVEN
    instrument.serial.stopbits = 1
    instrument.serial.timeout = 3
    instrument.serial.close_after_each_call = True
    log.info(f'Modbus ID Initialized: {i}')
    return instrument


def get_em_values(unitId):
    mb_client = initiate(unitId)
    for i in range(2):
        try:
            register_data = mb_client.read_registers(3960, 4, 3), True
            #register_data1 = mb_client.read_registers(3967, 1, 3), True
            log.info(f'register data is {register_data}')
            return register_data[0]
        except Exception as e:
            log.error(f"ERROR:{e}")


    return None


# endregion



if __name__ == '__main__':
    while True:
        a=get_em_values(1)
        log.info(f'[++++] different device {a[0]}   and r2 is {a[1]}')
        data1 = combine_cdab(a[0],a[1])
        log.info(f'[++++] kwh power data is {data1}')
        time.sleep(5)