import os
import sys
import pymysql
import yaml
from datetime import datetime

class Dao:
	def __init__(self, asset):
		db_login = None
		with open('credentials.yaml') as file:
			login = yaml.load(file, Loader=yaml.FullLoader)['mysqldb']
		self.connection = pymysql.connect(host=login['host'], user=login['user'], passwd=login['password'])
		self.cursor = self.connection.cursor()
		self.cursor.execute("USE stocks;")


	def close(self):
		self.cursor.close()
		self.connection.close()


	def add_candle(self, exchange, market, date_time, open_, high, low, close, volume):
		if type(date_time) != str:
			date_time = datetime.strftime(date_time, "%Y-%m-%d %H:%M:%S")
		query = "INSERT IGNORE INTO candles VALUES ('%s', '%s', '%s', %f, %f, %f, %f, %f);"\
			%(exchange, market, date_time, float(open_), float(high), 
			float(low), float(close), float(volume))
		self.cursor.execute(query)
		self.connection.commit()


	def get_candles(self, market, date=None):
		if date:
			query = "SELECT * FROM candles WHERE market='%s' AND date_time LIKE '%s __:__:__';"%(market, date)
		else:
			query = "SELECT * FROM candles WHERE market='%s';"%(market)
		self.cursor.execute(query)
		return self.cursor.fetchall()