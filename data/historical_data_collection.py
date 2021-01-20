import sqlite3
import time
import sys
import os
from datetime import datetime, timedelta
from candle import Candle
from api import Bittrex
from dao import Dao

MARKETS = [
	'BTC-USDT', 'ETH-USDT', 'ADA-USDT', 'XLM-USDT', 'LINK-USDT', 'DOT-USDT', 'LTC-USDT', 'NEO-USDT',
	'TRX-USDT', 'BSV-USDT', 'BCH-USDT', 'ENJ-USDT', 'LBC-USDT', 'BAT-USDT', 'ETC-USDT', 'DGB-USDT',
	'DOGE-USDT', 'EOS-USDT', 'XTZ-USDT', 'ALGO-USDT', 'ATOM-USDT', 'RVN-USDT'
]

if __name__ == '__main__':
	bittrex = Bittrex()
	print("Opening database connection")
	db = Dao()

	try:
		db.create_table()
	except sqlite3.OperationalError:
		pass
    
	one_year_ago = datetime.now() - timedelta(days=365)
	for market in MARKETS:
		while one_year_ago < datetime.now():
			time.sleep(1)
			print("Requesting candles for market {} on {} from Bittrex API".format(market, datetime.strftime(one_year_ago, "%Y-%m-%d")))
			candles = bittrex.get_historical_candles(
				symbol=market, candle_interval='MINUTE_5', candle_type='TRADE', year=one_year_ago.year,
				month=one_year_ago.month, day=one_year_ago.day
			)
			print("Adding candles for market {} on {} to SQLite database".format(market, datetime.strftime(one_year_ago, "%Y-%m-%d")))
			cndl_cnt = 0
			for candle in candles:
				next_candle = Candle(market=market, btrx_dict=candle)
				db.add_candle(next_candle)
				cndl_cnt += 1
			print("Added {} candles to database".format(cndl_cnt))
			one_year_ago = one_year_ago + timedelta(days=1)

	print("Closing database connection")
	db.close_connection()