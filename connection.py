import logging
import sys
import time

import serial
import serial.tools.list_ports

target_product = '"BBC micro:bit CMSIS-DAP"'
microbit = None
logger = logging.getLogger(__name__)
mb_loger = logging.getLogger("micro: bit")


# Base class for other connection exceptions
class ConnectionException(Exception):
    pass


class NotConnected(ConnectionException):
    def __init__(self, message="", method=None):
        self.message = message
        self.method = method
        super().__init__(self.message)

    def __str__(self):
        if self.method == "w":
            return self.message + "No connection found when writing data"
        elif self.method == "r":
            return self.message + "No connection found when reading data"
        elif self.method == "c":
            return self.message + "Connection lost when checking"


def connect():
    global microbit
    if microbit: return
    logger.info("Searching for device with product %s", target_product)
    devices = [port for port in serial.tools.list_ports.comports() if port.product == target_product]
    if len(devices) > 0:
        microbit = serial.Serial(devices[0].device, baudrate=115200)
        time.sleep(1)
        write("Connect")
        logger.info("Connecting device %s", devices[0])
    else:
        while True:
            time.sleep(0.5)
            devices = [port for port in serial.tools.list_ports.comports() if port.product == target_product]
            if len(devices) > 0:
                microbit = serial.Serial(devices[0].device, baudrate=115200)
                time.sleep(1)
                write("Connect")
                logger.info("Connecting device %s", devices[0])

                break

def disconnect():
    microbit.close()


def write(msg):
    global microbit
    if microbit is None:
        raise NotConnected(method="r")
    try:
        microbit.write(bytes(msg + '#', encoding="ascii"))
        logger.info("Wrote message \"%s\"", msg)
    except (serial.serialutil.SerialException, OSError):
        raise NotConnected(method="w")


def read():
    global microbit
    if microbit is None:
        e = NotConnected(method="r")
        logger.exception(e)
        return e
    try:
        msg = microbit.readline().decode('ascii').strip()
        mb_loger.info(msg)
        return msg
    except (serial.serialutil.SerialException, OSError):
        e = NotConnected(method="r")
        logger.exception(e)
        return e


if __name__ == "__main__":
    # Logging configuration
    with open("logging_config.json", "r") as file:
        config = json.load(file)
    logging.config.dictConfig(config["debug"])
    logger = logging.getLogger(__name__)
    logger.warning("Running in debug mode")

    connect()
    time.sleep(2)
    print(read())
    time.sleep(2)
    disconnect()