import serial
from time import sleep
import serial.tools.list_ports
import os
import re
import ast
import requests
import logging.handlers
from logging.handlers import TimedRotatingFileHandler

# Setting up Rotating file logging
dirname = os.path.dirname(os.path.abspath(__file__))

log_level = logging.INFO

FORMAT = ('%(asctime)-15s %(levelname)-8s %(module)-15s:%(lineno)-8s %(message)s')

logFormatter = logging.Formatter(FORMAT)
log = logging.getLogger("cremica_logs")

# checking and creating logs directory here
if not os.path.isdir("./logs"):
    log.info("[-] logs directory doesn't exists")
    try:
        os.mkdir("./logs")
        log.info("[+] Created logs dir successfully")
    except Exception as e:
        log.error(f"[-] Can't create dir logs Error: {e}")

fileHandler = TimedRotatingFileHandler(os.path.join(dirname, f'logs/app_log'),
                                       when='midnight', interval=1)
fileHandler.setFormatter(logFormatter)
fileHandler.suffix = "%Y-%m-%d.log"
log.addHandler(fileHandler)

consoleHandler = logging.StreamHandler()
consoleHandler.setFormatter(logFormatter)
log.addHandler(consoleHandler)
log.setLevel(log_level)
#
send_data = True
ACCESS_TOKEN = '4hzxPf6jtgyvvLigEB3e'
host_ip = '192.168.102.152'
HOST = f'http://{host_ip}:9080/api/v1/{ACCESS_TOKEN}/telemetry'
HEADERS = {'content-type': 'application/json'}
PREV_WT = 0
try:
    PORT_WT = usb_ports[0]
    wt_ser = serial.Serial(
        port=PORT_WT,
        baudrate=1200,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.EIGHTBITS,
        xonxoff=False,
        timeout=1,
        write_timeout=1
    )
except Exception as e:
    sleep(10)
    log.error(f'ERROR: {e} Error in opening serial port')


def read_weight():
    global PORT_WT, wt_ser
    try:
        wt_ser.flushOutput()
        wt_ser.flushInput()
        wt_ser.flush()
        weight = wt_ser.read_until()
        log.info(f"Got data --- {weight}")
        weight = weight.decode("utf-8")
        weight = re.sub(r"[^\d\.]", "", weight)
        weight = float(weight)
        log.info(f"Got weight data --- {weight}")
        return weight
    except Exception:
        try:
            sleep(2)
            wt_ser.flushOutput()
            wt_ser.flushInput()
            wt_ser.flush()
            wt_ser.close()
        except:
            pass
        try:
            # ports = serial.tools.list_ports.comports()
            # usb_ports = [p.device for p in ports if "USB" in p.device]
            # log.info(usb_ports)
            PORT_WT = 'COM1'  # usb_ports[1]
            wt_ser = serial.Serial(
                port=PORT_WT,
                baudrate=9600,
                parity=serial.PARITY_NONE,
                stopbits=serial.STOPBITS_ONE,
                bytesize=serial.EIGHTBITS,
                xonxoff=False,
                timeout=1,
                write_timeout=1
            )
            weight = wt_ser.read_until()
            weight = str(weight).replace("N", "").strip("'").replace(r"\\xaH\\xf8N", "").replace(r"=kg", "").replace(r"\\r\\n", "")
            weight = float(weight)
            return weight
        except Exception as e:
            log.error(f'ERROR: {e} Error in opening weight serial port')
            return "Error"


def post(payload):
    """posting an error in the attributes if the data is None"""
    global HEADERS
    url = f'{HOST}'
    # payload = {"Recorded_weight": Weight}
    log.info(str(payload))
    if send_data:
        try:
            request_response = requests.post(url, json=payload, headers=HEADERS, timeout=2)
            log.info(f"[+] {request_response.status_code}")
        except Exception as error:
            log.error(f"{error}")

# usb_ports = [p.device for p in ports if "USB" in p.description]
# log.info(f'every port is {usb_ports}')
#
# PORT_WT = usb_ports[0]
def read_barcode():
    # Replace 'COM3' with your actual port (e.g., '/dev/ttyUSB0' for Linux)
    ports = serial.tools.list_ports.comports()
    port = [p.device for p in ports if "USB" in p.description]
    log.info(f'scanner port is {port}')
    PORT_WT = usb_ports[0]
    baud_rate = 9600  # Typically, barcode scanners use 9600 baud rate
    # Open the serial port
    with serial.Serial(PORT_WT, baud_rate, timeout=1) as ser:
        log.info(f"Connected to {ser.name}")
        try:
            if ser.in_waiting > 0:
                barcode_data = ser.readline().decode('utf-8').strip()
                print(barcode_data)
                return barcode_data  # Return the barcode data
        except Exception as e:
            log.error(f"Error: {e}")
            return None  # Return None if an error occurs


def extract_mrn_and_desc(input_str):
    # Split the string into parts
    parts = input_str.split()

    # The last part is the MRN number
    mrn_no = parts[-1]

    # The rest is the description
    rm_desc = ' '.join(parts[:-1])

    return rm_desc, mrn_no


if __name__ == '__main__':
    log.info("Started....")
    while True:
        try:
            weight = read_weight()
            log.info(weight)
            if weight > 0:
                # weight = float(weight)
                log.info(f"got weight {weight}")
                weight_payload = {'weight': weight}
                post(weight_payload)
                sleep(1)
        except Exception as e:
            log.error(e)
        try:
            scanner_data = read_barcode()
            log.info(f'scanner data is {scanner_data}')
        except Exception as e:
            log.error(f'scanning data from barcode {e}')
        try:
            if scanner_data:
                converted_dict = ast.literal_eval(scanner_data)
                log.info(type(converted_dict))
                # Regular expression to find the dictionary part
                try:
                    # Access the dictionary values
                    rm_desc = converted_dict.get('rm_desc', '')
                    mrn_no = converted_dict.get('mrn_no', '')
                    mrn_no = '$' + mrn_no + '$'
                    print(mrn_no)
                    output = f"{rm_desc} {mrn_no}"

                    payload = {'rm_desc': rm_desc,
                               'mrn_no': str(mrn_no)}
                    post(payload)
                    log.info(f'[+] sending data of used coil {output}')
                except (SyntaxError, ValueError) as e:
                    log.error(f"Error converting string to dictionary: {e}")
        except Exception:
            rm_desc1, mrn_no1 = extract_mrn_and_desc(scanner_data)
            mrn_no1 = '$' + mrn_no1 + '$'

            payload1 = {'rm_desc': rm_desc1, 'mrn_no': mrn_no1}
            post(payload1)
            log.info(f'[+] sending data of new coil  {payload1}')
            sleep(5)
        sleep(5)

if __name__ == '__main__':
    while True:
        weight = [0,0,0,0,0,0,10.2,12.5,15.2,16.5,41.0,153.2,0]
        for i in weight:
            log.info(i)
            if i > 0:
                # i = float(i)
                if i < PREV_WT:
                    log.info(f'PREV_WT {PREV_WT}')
                    log.info(f"got i {i}")
                    i_payload = {'i': i}
                    print(i_payload)
                    PREV_WT = i
                if i == PREV_WT:
                    print('done')
                    PREV_WT = i
                else:
                    log.info(f'PREV_WT {PREV_WT}')
                    PREV_WT = i
                    print('break')
        sleep(1)