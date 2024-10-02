import os
import time
import minimalmodbus
import serial
import serial.tools.list_ports
import logging.config
import requests

logging.config.fileConfig('logging.config')
log = logging.getLogger('UPS_log')


# region Rotating Logs
dirname = os.path.dirname(os.path.abspath(__file__))


# reion Global Variables
GL_SEND_DATA = True
SAMPLE_RATE = 5
HEADERS = {"Content-Type": "application/json"}

EM_API = 'https://iot.ithingspro.cloud/ups/api/v1/forging/update_weight'

METER_ID = ''
LINE = ''


def post_em_values(payload: dict):
    if GL_SEND_DATA:
        try:
            send_req = requests.post(EM_API, json=payload, headers=HEADERS, timeout=2)
            logging.info(payload)
            logging.info(send_req.status_code)
            logging.info(send_req.text)
            send_req.raise_for_status()
            return True
        except Exception as e:
            logging.info(f"[-] Error in sending data of trolley weight TO API, {e}")
            return False


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
    for i in range(5):
        try:
            register_data = mb_client.read_registers(3960, 2, 3), True
            log.info(f'register data is {register_data}')
            if register_data:
                kwh_value = combine_cdab(*register_data)
                return kwh_value
        except Exception as e:
            log.error(f"ERROR:{e}")
    return None
# endregion


if __name__ == '__main__':
    try:
        while True:
            a=get_em_values(1)
            log.info(f'[++++] different device {a[0]}   and r2 is {a[1]}')
            data1 = combine_cdab(a[0],a[1])
            log.info(f'[++++] kwh power data is {data1}')
            time.sleep(5)
    except Exception as e:
        log.error(f"[-] Error While running program {e}")