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

DATA_SLICE_DAYS = 1
DATETIME_FORMAT = "%Y-%m-%dT%H:%M"

#CRYPTO = ['bitcoin','ethereum','solana','polkadot']
CRYPTO = ['BTC','ETH','SOL','DOT','OMI','BAN','MOON']
#CRYPTO = ['BTC']

def get_dummy_data():
    logger.info('Generating dummy data')

def fetch_prices(token):
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
    logger.info(geckourlhistorical)
    rawtimeseries = requests.get(geckourlhistorical).json()
    logger.info("Got price for the last "+str(days_ago)+" days from CoinGecko")
    timeseriesarray = rawtimeseries['prices']
    prices = []
    length=len (timeseriesarray)
    i=0
    while i < length:
        prices.append(timeseriesarray[i][1])
        i+=1
    # Get 24H Change
    geckourl24h = "https://api.coingecko.com/api/v3/simple/price?ids=" +str(tokenname)+"&vs_currencies=usd&include_24hr_change=true"
    logger.info(geckourl24h)
    raw24h = requests.get(geckourl24h).json()
    actual24h = raw24h[str(tokenname)]['usd_24h_change']
    liveprice = raw24h[str(tokenname)]['usd']
    # Add values to list
    prices.append(liveprice)
    prices.append(actual24h)
    prices.append(token)
    return prices

def main():
    logger.info('Initialize')

    data_sink = Observable()
    builder = Builder(config)
    builder.bind(data_sink)

    try:
        while True:
            try:
                for coin in itertools.cycle(CRYPTO):
                    prices = [entry[1:] for entry in get_dummy_data()] if config.dummy_data else fetch_prices(coin)
                    data_sink.update_observers(prices)
                    time.sleep(60)
            except (HTTPError, URLError) as e:
                logger.error(str(e))
                time.sleep(5)
    except IOError as e:
        logger.error(str(e))
    except KeyboardInterrupt:
        logger.info('Exit')
        data_sink.close()
        exit()


if __name__ == "__main__":
    main()
