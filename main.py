import getopt
import json
import logging
import logging.config
import sys
import threading

import connection
import data

debug = False
city = ""
log_path = ""
try:
    opts, args = getopt.getopt(sys.argv[1:], "-h-d-c:", ["help", "debug", "city="])
except getopt.GetoptError:
    print(sys.argv[0], "[-h] [-d|--debug] [-c <city name> | --city <city name>]")
    sys.exit(2)

for opt, arg in opts:
    if opt == '-h':
        print(sys.argv[0], "[-h] [-d|--debug] [-c <city name> | --city <city name>]")
        sys.exit()
    elif opt in ("-d", "--debug"):
        debug = True
    elif opt in ("-c", "--city"):
        city = arg

# Logging configuration
with open("logging_config.json", "r") as file:
    config = json.load(file)
if debug:
    logging.config.dictConfig(config["debug"])
else:
    logging.config.dictConfig(config["product"])
logger = logging.getLogger(__name__)
if debug: logger.warning("Running in debug mode")

# Obtain the city’s url
if city == "":
    city = input("Please input your city name: ")
url = data.get_url(city)
logger.info("Weather data will be from city %s, url gotten is %s", city, url)

connection.connect()

### MAIN ###
while True:
    try:
        msg = connection.read()
    except KeyboardInterrupt:
        logging.info("Shutting down Weather Service...")
        connection.disconnect()
        logging.info("Disconnected micro:bit serial device")
        sys.exit()

    if msg == "Request":
        threading.Thread(
            target=lambda: connection.write(data.load(url))
        ).start()
