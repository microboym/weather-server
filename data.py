import getopt
import json
import logging.config
import re
import sys

import lxml.etree
import requests

kind_data = {}
logger = logging.getLogger(__name__)


def load(url):
    logger.info("Loading weather data from %s", url)
    response = requests.get(url)
    response.encoding = "utf-8"
    page = lxml.etree.HTML(response.text)

    temperatures1 = page.xpath("//*[@class='tem']/span/text()")
    temperatures1 = list(map(lambda x: x.rstrip("℃"), temperatures1))  # remove the last symbol "℃"
    logger.debug("temperatures1: %s", temperatures1)

    temperatures2 = page.xpath("//*[@class='tem']/i/text()")
    temperatures2 = list(map(lambda x: x.rstrip("℃"), temperatures2))  # remove the last symbol "℃"
    logger.debug("temperatures2: %s", temperatures2)

    kinds = page.xpath("//*[@class='wea']/text()")
    regex = r"^([\u4e00-\u9fa5]+?)(\u8f6c([\u4e00-\u9fa5]+))?$" # 晴转多云
    kind_turples = list(map(lambda x: re.match(regex, x).group(1, 3), kinds))
    logger.debug("weather kinds: %s", kind_turples)

    results = list(map(encode, temperatures1, temperatures2, kind_turples)) # encode all data
    logger.info("Loaded data %s", results)
    return results[0]


def encode(temp1, temp2, kinds):
    if len(kinds) != 2:
        raise Exception(f"Number of kinds isn’t 2, got {len(kinds)}")
    if temp2 < temp1:
        swap = temp2
        temp2 = temp1
        temp1 = swap
    if kinds[1]:
        return f"Weather:{kind_data[kinds[0]]}{kind_data[kinds[1]]}-{temp1}-{temp2}"
    else:
        return f"Weather:{kind_data[kinds[0]]}-{temp1}-{temp2}"


def get_url(city_name):
    search = f"http://toy1.weather.com.cn/search?cityname={city_name}".encode("utf-8")
    response = json.loads(requests.get(search).text[1:-1])
    if len(response) > 1:
        print(f"--- Found {len(response)} Results of {city_name}:")
        i = 0
        for city in response:
            i += 1
            splited = city['ref'].split('~')
            print(f"---  {i}: {splited[0]} -- {splited[2]} {splited[4]} {splited[9]}")
        num = int(input("--- Enter city index or full name: "))
        if num < len(response):
            id = response[num - 1]['ref'].split('~')[0]
        else:
            id = num
    else:
        id = response[0]['ref'].split('~')[0]
    return f"http://www.weather.com.cn/weather/{id}.shtml"


# Load weather kinds
with open("kind.json", mode="r") as file:
    kind_data = json.load(file)

if __name__ == "__main__":
    # Get arguments
    city = ""
    try:
        opts, args = getopt.getopt(sys.argv[1:], "-h-c", ["help", "city="])
    except getopt.GetoptError:
        print(sys.argv[0], "[-c <city name>|--city=<city name>]")
        sys.exit(2)

    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print(sys.argv[0], "[-c <city name>|--city=<city name>]")
            sys.exit()
        elif opt in ("-c", "--city"):
            city = arg

    # Logging configuration
    with open("logging_config.json", "r") as file:
        config = json.load(file)
    logging.config.dictConfig(config["debug"])
    logger = logging.getLogger(__name__)
    logger.warning("Running in debug mode")

    # Obtain the city’s url
    if city == "":
        city = input("Please input your city name: ")
    url = get_url(city)
    logger.info("Weather data will be from city %s, url gotten is %s", city, url)

    # Load data
    print(load(url))
