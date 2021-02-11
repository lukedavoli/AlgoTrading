import time
import yaml
import sys
import os
import pandas as pd
import logging
from datetime import datetime, timedelta, date
from io import StringIO

from alphavantage_api import AlphaVantage
sys.path.insert(2, os.path.join(sys.path[0], '../..'))
from candle import Candle
from dao import Dao

logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    av = AlphaVantage()
    db = Dao(asset='stocks')

    MARKET = 'CCL'

    for y in range(1,3):
        for m in range(1, 13):
            candles = av.get_intraday_extended(symbol=MARKET, year=y, month=m)
            for candle in candles:
                db.add_candle(
                    market=MARKET, date_time=candle['date_time'], open_=candle['open'], 
                    high=candle['high'], low=candle['low'], close=candle['close'], 
                    volume=candle['volume']
                )
                logging.info("Candle ({}|{}) added to database".format(MARKET, candle['date_time']))

    