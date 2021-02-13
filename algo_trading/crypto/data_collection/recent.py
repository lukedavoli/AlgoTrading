import yaml
import time
import sys
import os
from datetime import datetime

from bittrex_api import Bittrex
sys.path.insert(2, os.path.join(sys.path[0], '..'))
from dao import Dao

MARKETS = ['RVN-USDT']

if __name__ == '__main__':
	if len(sys.argv) > 1 and sys.argv[1] == 'tofile':
		# Redirect standard output to file in db_updates folder
		db_updt_path = 'data_collection/db_updates'
		if not os.path.exists(db_updt_path): os.makedirs(db_updt_path)
		date_time = datetime.now().strftime("%Y-%m-%d_%H-%M")
		sys.stdout = open('{}/{}.txt'.format(db_updt_path, date_time), 'w')

	# Create API object
	bittrex = Bittrex()

	# Open connection with database
	print("Opening database connection")
	db = Dao(asset='crypto')

	# Request recent data from Bittrex API and add it to the database
	for market in MARKETS:
		time.sleep(1)
		print("Requesting candles for market {} from Bittrex API".format(market))
		candles = bittrex.get_recent_candles(
			symbol=market, candle_interval='MINUTE_5', candle_type='TRADE'
		)
		print("Adding candles for market {} to MySQL database".format(market))
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

	print("Closing database connection")
	db.close()