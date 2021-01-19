import sqlite3
import time
import sys
import os
from datetime import datetime
from candle import Candle
from api import Bittrex
from dao import Dao

MARKETS = [
	'BTC-USDT', 'ETH-USDT', 'ADA-USDT', 'XLM-USDT', 'LINK-USDT', 'DOT-USDT', 'LTC-USDT', 'NEO-USDT',
	'TRX-USDT', 'BSV-USDT', 'BCH-USDT', 'ENJ-USDT', 'LBC-USDT', 'BAT-USDT', 'ETC-USDT', 'DGB-USDT',
	'DOGE-USDT', 'EOS-USDT', 'XTZ-USDT', 'ALGO-USDT', 'ATOM-USDT', 'RVN-USDT'
]

if __name__ == '__main__':
	db_updt_path = 'db_updates'
	if not os.path.exists(db_updt_path): os.makedirs(db_updt_path)
	date_time = datetime.now().strftime("%Y-%m-%d_%H-%M")
	sys.stdout = open('{}/{}.txt'.format(db_updt_path, date_time), 'w')

	bittrex = Bittrex()
	print("Opening database connection")
	db = Dao()

	try:
		db.create_table()
	except sqlite3.OperationalError:
		pass

	for market in MARKETS:
		time.sleep(1)
		print("Requesting candles for market {} from Bittrex API".format(market))
		candles = bittrex.get_candles(
			symbol=market, candle_interval='MINUTE_5', candle_type='TRADE'
		)
		print("Adding candles for market {} to SQLite database".format(market))
		cndl_cnt = 0
		for candle in candles:
			next_candle = Candle(market=market, btrx_dict=candle)
			db.add_candle(next_candle)
			cndl_cnt += 1
		print("Added {} candles to database".format(cndl_cnt))

	print("Closing database connection")
	db.close_connection()