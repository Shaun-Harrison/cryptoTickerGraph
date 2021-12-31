import numpy as np
import requests
import os
import dateparser
import pytz
import json
import random
import time
import itertools
from datetime import datetime, timezone, timedelta
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from config.builder import Builder
from config.config import config
from logs import logger
from presentation.observer import Observable

import paho.mqtt.client as mqtt

DATA_SLICE_DAYS = 1
DATETIME_FORMAT = "%Y-%m-%dT%H:%M"
CRYPTO = ['BTC','ETH','SOL','DOT','OMI','BAN','MOON']
broker_url = "192.168.1.251"#MQTT server IP
broker_port = 1883 #MQTT server port
client = mqtt.Client()
deviceName= "RPI0Crypto"

def get_dummy_data():
    logger.info('Generating dummy data')

def fetch_prices(token):
    try:
        client.publish(topic="homeassistant/crypto/" + deviceName +  "/" + deviceName + token + "/config", payload='{"name":"' + deviceName + token + '","state_topic":"crypto/ticker/' + deviceName + '/state","unit_of_measurement":"$","value_template":"{{ value_json.' + token.lower() + '}}","unique_id":"'+ deviceName.lower() + '_' + token.lower() + '","device":{"identifiers":["' + deviceName.lower() + '_crypto"],"name":"' + deviceName + 'Crypto","model":"RPI ' + deviceName + '","manufacturer":"RPI"}}', qos=1, retain=True)
        days_ago = DATA_SLICE_DAYS
        endtime = int(time.time())
        starttime = endtime - 60*60*24*days_ago
        starttimeseconds = starttime
        endtimeseconds = endtime
        if token == "BTC":
            tokenname = "bitcoin"
        elif token == "ETH":
            tokenname = "ethereum"
        elif token == "SOL":
            tokenname = "solana"
        elif token == "DOT":
            tokenname = "polkadot"
        elif token == "OMI":
            tokenname = "ecomi"
        elif token == "BAN":
            tokenname = "banano"
        elif token == "MOON":
            tokenname = "moon"
        else:
            print("Unknown Token, please add to if statement")
            exit()
        geckourlhistorical = "https://api.coingecko.com/api/v3/coins/"+str(tokenname)+"/market_chart/range?vs_currency=usd&from="+str(starttimeseconds)+"&to="+str(endtimeseconds)
#       logger.info(geckourlhistorical)
        rawtimeseries = requests.get(geckourlhistorical).json()
#       logger.info(str(rawtimeseries))
        timeseriesarray = rawtimeseries['prices']
        prices = []
        length=len (timeseriesarray)
        i=0
        while i < length:
            prices.append(timeseriesarray[i][1])
            i+=1
        # Get 24H Change
        geckourl24h = "https://api.coingecko.com/api/v3/simple/price?ids=" +str(tokenname)+"&vs_currencies=usd&include_24hr_change=true"
#       logger.info(geckourl24h)
        raw24h = requests.get(geckourl24h).json()
        actual24h = raw24h[str(tokenname)]['usd_24h_change']
        liveprice = raw24h[str(tokenname)]['usd']
        # Publish Value to MQTT
        logger.info("Publishing to MQTT")
        client.publish(topic="crypto/ticker/" + deviceName + "/state", payload='{"'+ token.lower() +'":"'+ str(liveprice) +'"}', qos=1, retain=False)
        # Add values to list
        prices.append(liveprice)
        prices.append(actual24h)
        prices.append(token)
        return prices
    except:
        logger.info("Unexpected error")
        return ("null")
def main():
    logger.info('Initialize')

    data_sink = Observable()
    builder = Builder(config)
    builder.bind(data_sink)
    client.connect(broker_url, broker_port)

    while True:
        for coin in itertools.cycle(CRYPTO):
            try:
                prices = fetch_prices(coin)
                if prices != "null":
                    data_sink.update_observers(prices)
                    time.sleep(300)
            except (HTTPError, URLError) as e:
                logger.info(str(e))
                time.sleep(5)
            except KeyboardInterrupt:
                logger.info('Exit')
                data_sink.close()
                exit()

if __name__ == "__main__":
    main()
