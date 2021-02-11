import requests
import json
import yaml
import logging

class AlphaVantage:
    def __init__(self):
        self.API_BASE_URL = 'https://www.alphavantage.co/query'
        with open('credentials.yaml') as file:
            self.apikey = yaml.load(file, Loader=yaml.FullLoader)['alphavantage']['apikey']
        
    def get_intraday_extended(self, symbol, year, month, interval='5min', adjusted=True):
        candles = []
        querystring = {
            'interval': interval,
            'function': 'TIME_SERIES_INTRADAY_EXTENDED',
            'symbol': symbol,
            'slice': 'year{}month{}'.format(year, month),
            'apikey': self.apikey
        }
        logging.info("Requesting extended intraday data for symbol {} in slice " 
            "year{}month{}".format(symbol, year, month))
        response = requests.get(url=self.API_BASE_URL, params=querystring)
        rows = response.text.splitlines()
        rows.pop(0)
        logging.info("Candles for year{}month{}: {}".format(year, month, len(rows)))
        for row in rows:
            data = row.split(',')
            candles.append(dict(date_time=data[0], open=data[1], high=data[2], low=data[3], close=data[4], volume=data[5]))
        return candles

