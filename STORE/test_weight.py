from time import sleep
import serial.tools.list_ports
import serial
import re
import requests

ports = serial.tools.list_ports.comports()
usb_ports = [p.device for p in ports if "USB" in p.hwid or "ttyUSB" in p.device or "ttyACM" in p.device]
print(usb_ports)
PORT_WT = usb_ports[0]
print(PORT_WT)
send_data = True

# PORT_WT = '/dev/ttyUSB0'
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


def read_weight():
    global PORT_WT, wt_ser
    try:
        wt_ser.flushOutput()
        wt_ser.flushInput()
        wt_ser.flush()
        weight = wt_ser.read_until()
        print(f"Got data --- {weight}")
        #eight = weight.decode("utf-8")
        weight = weight.decode('utf-8', errors='replace')
        weight = re.sub(r"[^\d\.]", "", weight)
        weight = float(weight)
        print(f"Got weight data --- {weight}")
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
            # PORT_WT = '/dev/ttyUSB0'
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
            weight = weight.decode("utf-8")
            weight = re.sub(r"[^\d\.]", "", weight)
            weight = float(weight)
            print(f"Got weight data --- {weight}")
            return weight
        except Exception as e:
            print(f'ERROR: {e} Error in opening weight serial port')
            return "Error"


def post(payload):
    """posting an error in the attributes if the data is None"""
    global HEADERS
    url = f'{HOST}'
    # payload = {"Recorded_weight": Weight}
    print(str(payload))
    if send_data:
        try:
            request_response = requests.post(url, json=payload, headers=HEADERS, timeout=2)
            print(f"[+] {request_response.status_code}")
        except Exception as error:
            print(f"{error}")


if __name__ == '__main__':
    print("Started....")
    while True:

        try:
            while True:
                weight = read_weight()
                print(weight)
                #if weight > 0:
                    # weight = float(weight)
                    # print(f"got weight {weight}")
                    # weight_payload = {'weight': weight}
                    # print(weight_payload)
                    #break
                sleep(5)
        except Exception as e:
            print(e)
        sleep(5)
