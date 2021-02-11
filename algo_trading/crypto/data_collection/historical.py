import time
import yaml
import sys
import os
from datetime import datetime, timedelta, date

from bittrex_api import Bittrex
sys.path.insert(2, os.path.join(sys.path[0], '../..'))
from candle import Candle
from dao import Dao

DAYS_AGO = int(sys.argv[1])
ROWS_PER_DAY = 288
MARKETS = ['RVN-USDT']

if __name__ == '__main__':
	# Create API object
	bittrex = Bittrex()

	# Open connection with database
	print("Opening database connection")
	db = Dao(asset='crypto')
	
	for market in MARKETS:
		one_year_ago = date.today() - timedelta(days=DAYS_AGO)
		while one_year_ago < datetime.utcnow().date():
			date_str = datetime.strftime(one_year_ago, "%Y-%m-%d")
			db_atdate = db.get_candles(market=market, date=date_str)
			if len(db_atdate) != ROWS_PER_DAY:
				time.sleep(1)
				print("Requesting candles for market {} on {} from Bittrex API".format(market, datetime.strftime(one_year_ago, "%Y-%m-%d")))
				candles = bittrex.get_historical_candles(
					symbol=market, candle_interval='MINUTE_5', candle_type='TRADE', year=one_year_ago.year,
					month=one_year_ago.month, day=one_year_ago.day
				)
				print("Adding candles for market {} on {} to database".format(market, datetime.strftime(one_year_ago, "%Y-%m-%d")))
				cndl_cnt = 0
				for candle in candles:
					dt_object = datetime.strptime(candle['startsAt'], "%Y-%m-%dT%H:%M:%SZ")
					date_time = datetime.strftime(dt_object, "%Y-%m-%d %H:%M:%S")
					db.add_candle(
						market=market, date_time=date_time, open_=candle['open'], 
						high=candle['high'], low=candle['low'], close=candle['close'], 
						volume=candle['quoteVolume']
					)
					cndl_cnt += 1
				print("Added {} candles to database".format(cndl_cnt))
			else:
				print("Database already has all rows for {} on {}, skipping".format(market, date_str))
			one_year_ago = one_year_ago + timedelta(days=1)

	print("Closing database connection")
	db.close()