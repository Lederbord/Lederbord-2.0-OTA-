import RPi.GPIO as GPIO
import requests
from subprocess import call
# import pydbus
# import gi

import os
import time



# Script to poll shutdown pin at a specified frequency

BALENA_SUPERVISOR_ADDRESS_ENV_NAME = "BALENA_SUPERVISOR_ADDRESS"
BALENA_SUPERVISOR_API_KEY_ENV_NAME = "BALENA_SUPERVISOR_API_KEY"

POLL_FREQUENCY_SECS = 3

SHUTDOWN_PIN_NUM = 15

TAG = "ShutdownLoop: "
DEBUG = True  # boolean to determine whether verbose output is given (true) or suppressed (false)

REAL = True  # boolean to control whether we really shutdown (for testing)

GPIO.setmode(GPIO.BCM)
GPIO.setup(SHUTDOWN_PIN_NUM, GPIO.IN, pull_up_down=GPIO.PUD_UP)

CONTROLLED_SHUTDOWN_ENV_NAME = "LEDERBORD_CONTROLLED_SHUTDOWN_ENABLED"
shutdown_enabled = os.getenv(CONTROLLED_SHUTDOWN_ENV_NAME, '0')


def shutdown_pi():
    if REAL and shutdown_enabled == '1':
        print("Performing Shutdown")

        #prepare for supervisor request
        headers = {
            "Content-Type": "application/json"
        }
        balena_supervisor_address = os.getenv(BALENA_SUPERVISOR_ADDRESS_ENV_NAME)
        balena_supervisor_api_key = os.getenv(BALENA_SUPERVISOR_API_KEY_ENV_NAME)
        balena_shutdown_request_endpoint = "{}/v1/shutdown?apikey={}".format(balena_supervisor_address,
                                                                             balena_supervisor_api_key)
        debug_print("Makling request to: {}".format(balena_shutdown_request_endpoint))
        resp = requests.post(balena_shutdown_request_endpoint, headers=headers)
        debug_print("Response: {}".format(resp))
        # bus = pydbus.SystemBus()
        # logind = bus.get('.login1')['.Manager']
        # logind.PowerOff(True)
    else:
        print("Performing FAKE shutdown (REAL boolean is set to False, or {} not true)".format(
            CONTROLLED_SHUTDOWN_ENV_NAME))
        input("Try again?") #stop the container from closing and then restarting...
    exit(0)


def debug_print(message: str):
    if DEBUG:
        print(TAG + message)


print("Script started, waiting for pin {} to go HI...".format(SHUTDOWN_PIN_NUM))



while True:
    print("Shutdown Loop Running")     
    value = GPIO.input(SHUTDOWN_PIN_NUM)
    debug_print("Read {} from pin {}".format(value, SHUTDOWN_PIN_NUM))
    if int(value) == 1:
        debug_print("HI was detected on pin {}. Shutting down...".format(SHUTDOWN_PIN_NUM))
        # value_file.close()
        print("Pi shutdown start")
        shutdown_pi()
    time.sleep(POLL_FREQUENCY_SECS)
