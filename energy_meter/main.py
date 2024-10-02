import requests
import schedule
import serial
import minimalmodbus
import time
import struct
import os
import datetime
import logging
import logging.handlers
from logging.handlers import TimedRotatingFileHandler
from ingeniousLib.utils import ConfReader
from pprint import pprint
import serial.tools.list_ports

# Setting up Rotating file logging
dirname = os.path.dirname(os.path.abspath(__file__))


log_level = logging.INFO

FORMAT = ('%(asctime)-15s %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')

logFormatter = logging.Formatter(FORMAT)
log = logging.getLogger("LOGS")

# checking and creating logs directory here
if not os.path.isdir("./logs"):
    log.info("[-] logs directory doesn't exists")
    try:
        os.mkdir("./logs")
        log.info("[+] Created logs dir successfully")
    except Exception as e:
        log.error(f"[-] Can't create dir logs Error: {e}")

fileHandler = TimedRotatingFileHandler(os.path.join(dirname, f'logs/em_log'),
                                       when='midnight', interval=1)
fileHandler.setFormatter(logFormatter)
fileHandler.suffix = "%Y-%m-%d.log"
log.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
log.addHandler(consoleHandler)
log.setLevel(log_level)


# region Configuration Initialization
HOST = ''
PASSWORD = ''
PORT = ''
USERNAME_ = ''
QUEUE = ''
SEND_DATA = ''
AMQP_DATA = ''
ACCESS_TOKEN = ''
MACHINE_NAME = ''
LINE_ID = ''
MACHINE_IP = ''

CONFDIR = f"{dirname}/conf"
log.info(f"configuration directory name is {CONFDIR}")
if not os.path.isdir(CONFDIR):
    log.info("[-] conf directory doesn't exists")
    try:
        os.mkdir(CONFDIR)
        log.info("[+] Created configuration dir successfully")
    except Exception as e:
        log.error(f"[-] Can't create dir configuration Error: {e}")

machine_config_file = f"{CONFDIR}/machine_config.csv"
server_config_file = f"{CONFDIR}/server_config.csv"

obj_conf_handler = ConfReader()
if not os.path.exists(machine_config_file):
    obj_conf_handler.create_empty_csv(machine_config_file, ['MACHINE_NAME',
                                                        'ACCESS_TOKEN',
                                                        'MACHINE_IP',
                                                        'LINE_ID'
                                                            ])
if not os.path.exists(server_config_file):
    obj_conf_handler.create_empty_csv(server_config_file, ['HOST', 'PORT', 'QUEUE', 'USERNAME', 'PASSWORD'])

# reading the config file to get the machine configuration
MACHINE_INFO = obj_conf_handler.parse_conf_csv(machine_config_file)
SERVER_INFO = obj_conf_handler.parse_conf_csv(server_config_file)
log.info(MACHINE_INFO)
log.info(SERVER_INFO)

if SERVER_INFO:
    HOST = SERVER_INFO[0]['HOST']
    PORT = SERVER_INFO[0]['PORT']
    QUEUE = SERVER_INFO[0]['QUEUE']
    USERNAME_ = SERVER_INFO[0]['USERNAME']
    PASSWORD = SERVER_INFO[0]['PASSWORD']

if MACHINE_INFO:
    ACCESS_TOKEN = MACHINE_INFO[0]['ACCESS_TOKEN']
    MACHINE_NAME = MACHINE_INFO[0]['MACHINE_NAME']
    LINE_ID = MACHINE_INFO[0]['LINE_ID']
    MACHINE_IP = MACHINE_INFO[0]['MACHINE_IP']

print(f"HOST         [{HOST}]")
print(f"PORT         [{PORT}]")
print(f"QUEUE        [{QUEUE}]")
print(f"USERNAME     [XX-REDACTED-XX]")
print(f"PASSWORD     [XX-REDACTED-XX]")
print(f"ACCESS_TOKEN [XX-REDACTED-XX]")
print(f"MACHINE_NAME [{MACHINE_NAME}]")
print(f"LINE_ID      [{LINE_ID}]")
print(f"MACHINE_IP   [{MACHINE_IP}]")

# endregion

# Setting up Rotating file logging
dirname = os.path.dirname(os.path.abspath(__file__))

#  Every -- Seconds send data to server
SAMPLE_RATE = 5
# To Stop sending data to server
GL_SEND_DATA = True


HEADERS = {"Content-Type": 'application/json'}
EMS_HOST = f'https://{HOST}/ups/api/v1/forging/update_weight'


machine_info = {
    'METER1': {
        'type_': 'EM',
        'machine_name':'ACFG03',
        'unitId': 83,
        'start_reg': 3960,
        'reg_length': 2,
        'pName': ['start_kwh', 'end_kwh'],
    },
}


def initiate(slaveId):
    # com_port = None
    # for i in range(5):
    #     try:
    #         ports = serial.tools.list_ports.comports()
    #         usb_ports = [p.device for p in ports if "USB" in p.description]
    #         log.info(usb_ports)
    #         com_port = usb_ports[1]
    #         break
    #     except Exception as e:
    #         log.info(f"[-] Error Can't Open Port {e}")
    #         com_port = None
    #         time.sleep(1)
    com_port = '/dev/serial/usb-FTDI_FT232R_USB_UART_AB0PN5N1-if00-port0'
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


def decode_ieee(val_int):
    return struct.unpack("f", struct.pack("I", val_int))[0]


def word_list_to_long(val_list, big_endian=True):
    # allocate list for long int
    long_list = [None] * int(len(val_list) / 2)
    # fill registers list with register items
    for i, item in enumerate(long_list):
        if big_endian:
            long_list[i] = (val_list[i * 2] << 16) + val_list[(i * 2) + 1]
        else:
            long_list[i] = (val_list[(i * 2) + 1] << 16) + val_list[i * 2]
    # return long list
    return long_list


def f_list(values, bit=True):
    fist = []
    for f in word_list_to_long(values, bit):
        fist.append(round(decode_ieee(f), 3))
    # log.info(len(f_list),f_list)
    return fist


def em_values():
    global headers
    for m_name, m_info in machine_info.items():
        log.info(f">>--------{m_name}------>")
        data = None
        data = get_em_values(m_info['unitId'], m_info['start_reg'], m_info['reg_length'], m_info['type_'])
        try:
            payload = {
                "meter": f"{m_name}_{m_info['machine_name']}",
                "line": LINE_ID,
                "start_kwh": 0,
                "end_kwh": 0
            }
            if data:
                payload["start_kwh"] = data[0]
                payload["end_kwh"] = data[0]
                post_energy_consumption(payload)
        except Exception as e:
            log.error(e)


schedule.every(SAMPLE_RATE).seconds.do(em_values)


def post_energy_consumption(payload: dict):
    if GL_SEND_DATA:
        try:
            send_req = requests.post(EMS_HOST, json=payload, headers=HEADERS, timeout=2)
            logging.info(payload)
            logging.info(send_req.status_code)
            logging.info(send_req.text)
            send_req.raise_for_status()
            return True
        except Exception as e:
            logging.info(f"[-] Error in sending data of trolley weight TO API, {e}")
            return False

def get_em_values(unitId, start, length, type_):
    mb_client = initiate(unitId)

    if type_ == 'EM':  # DONE
        for i in range(2):
            try:
                data0 = f_list(mb_client.read_registers(3960, 2, 3))
                register_data = data0
                log.info(len(register_data))
            except Exception as e:
                log.error(f"ERROR:{e}")
                register_data = []
                time.sleep(i / 10)
            if register_data:
                log.info(register_data)
                return register_data
    return None

#updated
# def post_data(payload, machine_id):
#     """posting OEE DATA to the SERVER"""
#     url = f'{HOST}/api/v1/{machine_info[machine_id]["access_token"]}/telemetry'
#     log.info("[+] Sending data to server")
#     if send_data:
#         try:
#             send_req = requests.post(url, json=payload, headers=headers, timeout=2)
#             log.info(send_req.status_code)
#             send_req.raise_for_status()
#             if SYNC_FLAG:
#                 sync_data = c.get_sync_data()
#                 pprint(sync_data)
#                 for row in sync_data:
#                     payload_sync = row.get('payload')
#                     date_sync = row.get('date_')
#                     hour_sync = row.get('hour_')
#                     machine_id_sync = row.get('machine_id')
#                     log.info(f"[+] ----- {machine_id_sync} - {date_sync} - {hour_sync}")
#                     log.debug(payload_sync)
#                     try:
#                         url = f'{HOST}/api/v1/{machine_info[machine_id_sync]["access_token"]}/telemetry'
#                         log.info(url)
#                         sync_req = requests.post(url, json=payload_sync, headers=headers, timeout=2)
#                         sync_req.raise_for_status()
#                         log.info(f"[+] clearing sync for -> {machine_id_sync} - {date_sync} - {hour_sync}")
#                         c.clear_sync_data(date_sync, hour_sync, machine_id_sync)
#                         with open(os.path.join(dirname, f'logs/sync_log{datetime.date.today()}.txt'), 'a') as f:
#                             pname = f'{datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")} ---- SYNC DONE\n'
#                             f.write(pname)
#                         time.sleep(0.1)
#                     except Exception as e:
#                         log.error(f"[-] Error in sending SYNC Cycle time data {e}")
#                     break
#                 else:
#                     log.info("(^-^) No data to sync")
#         except Exception as e:
#             date_ = datetime.datetime.now().strftime("%Y-%m-%d")
#             hour_ = datetime.datetime.now().hour
#             log.error(f"[-] Error in sending Cycle time data {e}")
#             if SYNC_FLAG and payload['machine_running']:
#                 c.add_sync_data(payload, machine_id, hour_, date_)


# def post_mb_error(m_name, accessToken, status):
#     """posting an error in the attributes if the data is None"""
#     global headers
#     try:
#         url = f'{HOST}/api/v1/{accessToken}/attributes'
#         payload = {"error": status}
#         log.info(f'"machineId:" {m_name} {str(payload)}')
#         if send_data:
#             request_response = requests.post(url, json=payload, headers=headers, timeout=5)
#             log.info(request_response.text)
#     except Exception as e:
#         log.error(f"Error while sending the status {e}")


try:
    while True:
        schedule.run_pending()
        time.sleep(1)
except KeyboardInterrupt:
    pass
except:
    time.sleep(10)
