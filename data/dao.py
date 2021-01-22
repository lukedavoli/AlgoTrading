import pymysql
from datetime import datetime

class Dao:
	def __init__(self, user, password, host, port):
		self.connection = pymysql.connect(host=host, user=user, passwd=password)
		self.cursor = self.connection.cursor()
		self.cursor.execute("USE crypto;")


	def close(self):
		self.cursor.close()
		self.connection.close()


	def add_candle(self, candle):
		date_time_str = datetime.strftime(candle.date_time, "%Y-%m-%d %H:%M:%S")
		query = "INSERT IGNORE INTO candles VALUES ('%s', '%s', %f, %f, %f, %f, %f);"\
			%(candle.market, date_time_str, float(candle.open_), float(candle.high), 
			float(candle.low), float(candle.close), float(candle.quote_volume))
		self.cursor.execute(query)
		self.connection.commit()


	def get_candles(self, market, date=None):
		if date:
			query = "SELECT * FROM candles WHERE market='%s' AND date_time LIKE '%s __:__:__';"%(market, date)
		else:
			query = "SELECT * FROM candles WHERE market='%s';"%(market)
		self.cursor.execute(query)
		return self.cursor.fetchall()