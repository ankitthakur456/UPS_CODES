import os
import logging
# import logging.config
import requests

# logging.config.fileConfig('logging.config')
log = logging.getLogger('UPS_log')
# region definding global var's
access_token = 'ogDKQumq3MFUCeqBsZZU'
host = 'iot.ithingspro.cloud'
HEADERS = {"Content-Type": "application/json"}
GL_SEND_DATA = True
API = 'https://iot.ithingspro.cloud/api/v1/ogDKQumq3MFUCeqBsZZU/telemetry'
PRODUCTION_WEIGHT_API = 'https://iot.ithingspro.cloud/ups/api/v1/forging/update_weight'


def send_trolley_weight(payload: dict):
    if GL_SEND_DATA:
        try:
            send_req = requests.post(API, json=payload, headers=HEADERS, timeout=2)
            logging.info(payload)
            logging.info(send_req.status_code)
            logging.info(send_req.text)
            send_req.raise_for_status()
            return True
        except Exception as e:
            logging.info(f"[-] Error in sending data of trolley weight TO API, {e}")
            return False


def send_production_weight(DATA: dict):
    if GL_SEND_DATA:
        try:
            send_req = requests.post(PRODUCTION_WEIGHT_API, json=DATA, headers=HEADERS, timeout=2)
            logging.info(DATA)
            logging.info(send_req.status_code)
            logging.info(send_req.text)
            send_req.raise_for_status()
        except Exception as e:
            logging.info(f"[-] Error in sending data of production weight TO API, {e}")


def send_work_order(DATA: dict):
    if GL_SEND_DATA:
        try:
            send_req = requests.post(API, json=DATA, headers=HEADERS, timeout=2)
            logging.info(DATA)
            logging.info(send_req.status_code)
            send_req.raise_for_status()
        except Exception as e:
            logging.info(f"[-] Error in sending data of work order TO API, {e}")


def send_coil_data(DATA: dict):
    if GL_SEND_DATA:
        try:
            send_req = requests.post(API, json=DATA, headers=HEADERS, timeout=2)
            logging.info(DATA)
            logging.info(send_req.status_code)
            send_req.raise_for_status()
        except Exception as e:
            logging.info(f"[-] Error in sending data of coil TO API, {e}")


def send_machine_status(DATA: dict):
    if GL_SEND_DATA:
        try:
            send_req = requests.post(API, json=DATA, headers=HEADERS, timeout=3)
            logging.info(DATA)
            logging.info(send_req.status_code)
            logging.info(send_req.text)
            send_req.raise_for_status()
        except Exception as e:
            logging.info(f"[-] Error in sending data of machine status TO telemetry, {e}")