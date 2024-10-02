import time
import os
from pyModbusTCP.client import ModbusClient
import logging


log = logging.getLogger('UPS_log')


class ModbusHelper:
    def __init__(self, ip='192.168.2.1', port=502):
        log.info(f"[+] Machine Params are : [{ip}]:[{port}]")
        self.ip = ip
        self.port = port

    def connection(self):
        c = ModbusClient(host=self.ip, port=self.port, unit_id=1, auto_open=True)
        return c


    def read_machine_status(self):
        try:
            for _ in range(5):
                c = self.connection()
                regs = c.read_coils(8192, 1)
                log.info(f"[+] Got Machine data {regs}")
                c.close()
                if not regs:
                    log.warning(f"[+] Got Machine data {regs}")
                else:
                    return regs[0]
        except Exception as err:
            log.error(f'[+] Error Machine disconnected {err}')
        return None


    def power_off_machine(self):
        try:
            c = self.connection()
            for i in range(5):
                log.info("[+] Trying to Turn Machine [OFF]")
                if c.write_single_coil(8193, True):
                    log.info(f"[+] Machine Stopped Successfully")
                    return True
        except Exception as err:
            log.error(f'Error PLC disconnected {err}')
        log.info("[-] Failed to Turn OFF the Machine....")