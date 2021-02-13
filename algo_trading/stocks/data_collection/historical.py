import time
import yaml
import sys
import os
import logging
from datetime import datetime, timedelta, date
from io import StringIO

from alphavantage_api import AlphaVantage
sys.path.insert(1, os.path.join(sys.path[0], '..'))
from dao import Dao

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    av = AlphaVantage()
    db = Dao(asset='stocks')

    MARKETS = [
        {'xchg': 'NASDAQ', 'symbol': 'AMZN'}, 
        {'xchg': 'NASDAQ', 'symbol': 'SBUX'}, 
        {'xchg': 'NYSE', 'symbol': 'BSBR'},
        {'xchg': 'NYSE', 'symbol': 'MCD'},
        {'xchg': 'NYSE', 'symbol': 'K'},
        {'xchg': 'NYSE', 'symbol': 'T'},
    ]

    for market in MARKETS:
        for y in range(1,3):
            for m in range(1, 13):
                candles = av.get_intraday_extended(symbol=market['symbol'], year=y, month=m)
                for candle in candles:
                    db.add_candle(
                        exchange=market['xchg'], market=market['symbol'], date_time=candle['date_time'], 
                        open_=candle['open'], high=candle['high'], low=candle['low'], 
                        close=candle['close'], volume=candle['volume']
                    )
                    logging.info("Candle ({}|{}) added to database".format(market, candle['date_time']))

    