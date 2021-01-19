import sqlite3
import time
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
	db = Dao()

	try:
		db.create_table()
	except sqlite3.OperationalError:
		pass


	for market in MARKETS:
		time.sleep(1)
		candles = bittrex.get_candles(
			symbol=market, candle_interval='MINUTE_5', candle_type='TRADE'
		)
		for candle in candles:
			next_candle = Candle(market=market, btrx_dict=candle)
			db.add_candle(next_candle)
	
	db.close_connection()