import serial.tools.list_ports
import serial
import logging.config
import os
import ast
import time
from sending_data import send_work_order, send_coil_data

if not os.path.isdir("./logs"):
    print("[-] logs directory doesn't exists")
    os.mkdir("./logs")
    print("[+] Created logs dir successfully")
# Set up logging configuration
logging.config.fileConfig('logging.config')
log = logging.getLogger('UPS_log')


def scaning():
    ports = serial.tools.list_ports.comports()
    port = [p.device for p in ports if "scanner" in p.hwid.lower() or "barcode" in p.hwid.lower()]
    port = port[0]

    log.info(port)
    baud_rate = 9600

    with serial.Serial(port, baud_rate, timeout=1) as ser:
        log.info(f"Connected to {ser.name}")
        while True:
            try:
                if ser.in_waiting > 0:
                    barcode_data = ser.readline().decode('utf-8').strip()

                    return barcode_data
            except Exception as e:
                log.error(f"Error: {e}")
                return None


def work_order_data():
    # Split the string into parts
    input_str = scaning()
    parts = input_str.split("-")
    log.info(parts)
    material_code = parts[0]
    work_order = parts[1]
    qty = parts[2]
    chease_wt = parts[3]
    chese_unit = parts[4]
    finish_wt = parts[5]
    finish_unit = parts[6]
    mrn_no = parts[7]
    if input_str:
        return material_code, work_order, qty, chease_wt, chese_unit, finish_wt, finish_unit, mrn_no
    else:
        return None


def sending_work_order():
    try:
        material_code, work_order, qty, chease_wt, chese_unit, finish_wt, finish_unit, mrn_no = work_order_data()
        work_order_payload = {
            "line": "string",
            "wo_number": work_order,
            "mrn_no": mrn_no,
            "material_code": material_code,
            "quantity": qty,
            "cheese_weight": chease_wt,
            "cw_parameter": chese_unit,
            "finish_weight": finish_wt,
            "fw_parameter": finish_unit,
            "machine_name": "string",
        }
        log.info(f'work order payload {work_order_payload}')
        send_work_order(work_order_payload)
        return True
    except Exception as e:
        log.error('error is in sending work order data')


def check_keys(data):
    # Check if both 'rm_desc' and 'mrn_no' are in the dictionary
    if 'rm_desc' in data and 'mrn_no' in data:
        return True
    else:
        return False



if __name__ == '__main__':
    log.info("Started....")
    while True:
        input_str = scaning()
        flag = False
        try:
            input_str1= str(input_str)
            clean_str = input_str1[1:-1]
            clean_str = ast.literal_eval(clean_str)
            log.info(clean_str)
            flag = check_keys(clean_str)
        except Exception as e:
            log.error(f'It is work order data {e}')
        log.info(flag)
        if flag:
            rm_desc = clean_str.get('rm_desc')
            mrn_no = clean_str.get('mrn_no')
            weight = clean_str.get('weight')

            coil_data_payload = {'rm_desc': rm_desc,
                                 'mrn_no': mrn_no,
                                 'weight': weight
                                 }
            send_coil_data(coil_data_payload)
        else:
            sending_work_order()
        time.sleep(5)
