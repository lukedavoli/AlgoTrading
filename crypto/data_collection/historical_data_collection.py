import time
import yaml
import sys
import os
from datetime import datetime, timedelta, date

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from candle import Candle
from api import Bittrex
from dao import Dao

DAYS_AGO = int(sys.argv[1])
ROWS_PER_DAY = 288
MARKETS = [
	'BTC-USDT', 'ETH-USDT', 'ADA-USDT', 'XLM-USDT', 'LINK-USDT', 'DOT-USDT', 'LTC-USDT', 'NEO-USDT',
	'TRX-USDT', 'BSV-USDT', 'BCH-USDT', 'ENJ-USDT', 'LBC-USDT', 'BAT-USDT', 'ETC-USDT', 'DGB-USDT',
	'DOGE-USDT', 'EOS-USDT', 'XTZ-USDT', 'ALGO-USDT', 'ATOM-USDT', 'RVN-USDT'
]

if __name__ == '__main__':
	# Create API object
	bittrex = Bittrex()

	# Open connection with database
	print("Opening database connection")
	db = Dao()
	
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
					next_candle = Candle(market=market, btrx_dict=candle)
					db.add_candle(next_candle)
					cndl_cnt += 1
				print("Added {} candles to database".format(cndl_cnt))
			else:
				print("Database already has all rows for {} on {}, skipping".format(market, date_str))
			one_year_ago = one_year_ago + timedelta(days=1)

	print("Closing database connection")
	db.close()