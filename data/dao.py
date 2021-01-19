import sqlite3
from  sqlite3 import Error

class Dao:
	def __init__(self):
		self.connection = self.create_connection('candles.db')
		self.cursor = self.connection.cursor()


	def create_connection(self, db_file):
		connection = None
		try:
			connection = sqlite3.connect(db_file)
			return connection
		except Error as e:
			print(e)

		return connection


	def close_connection(self):
		self.connection.close()


	def create_table(self):
		self.cursor.execute("""CREATE TABLE candles (
			market text, 
			date_time text, 
			open real, 
			high real, 
			low real, 
			close real,
			volume real, 
			quote_volume real,
			PRIMARY KEY (market, date_time)
		)""")
		self.connection.commit()


	def add_candle(self, candle):
		self.cursor.execute("""INSERT OR IGNORE INTO candles VALUES (
			:market, :date_time,
			:open, :high, :low, :close, 
			:volume, :quote_volume 
			)""",
			{
				'market': candle.market, 'date_time': candle.date_time,
				'open': candle.open_, 'high': candle.high, 'low': candle.low, 'close': candle.close,
				'volume': candle.volume, 'quote_volume': candle.quote_volume
			}
		)
		self.connection.commit()


	def get_candles_for_market(self, market):
		self.cursor.execute("SELECT * FROM candles WHERE market=:market", {'market': market})
		return self.cursor.fetchall()