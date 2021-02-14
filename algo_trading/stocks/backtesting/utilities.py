import backtrader as bt
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from dao import Dao

def get_candles(exchange, symbol, start_date, end_date):
    df_candles = None
    try:
        df_candles = pd.read_csv(
            '../candles/{}-{}.csv'.format(exchange, symbol), index_col='date_time', parse_dates=True
        )
    except FileNotFoundError:
        db = Dao()
        candles = db.get_candles(exchange=exchange, symbol=symbol)
        columns = ['exchange', 'symbol', 'date_time', 'open', 'high', 'low', 'close', 'volume']
        df_candles = pd.DataFrame(candles, columns=columns)
        df_candles.drop(columns=['exchange', 'symbol'], inplace=True)
        df_candles['date_time'] = pd.to_datetime(df_candles['date_time'])
        df_candles.set_index('date_time', inplace=True)
        df_candles.to_csv('../candles/{}-{}.csv'.format(exchange, symbol))
    if start_date:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        df_candles = df_candles[df_candles.index >= start_dt]
    if end_date:
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        df_candles = df_candles[df_candles.index <= end_dt]
    return df_candles


def calculate_pct_return(cerebro, cash):
    return ((cerebro.broker.getvalue() - cash) / cash) * 100


def get_benchmark(strategy, candles, symbol, cash, commission, bet_pct):
    cerebro_bmrk = bt.Cerebro()
    cerebro_bmrk.broker.setcash(cash)
    cerebro_bmrk.broker.setcommission(commission=commission)
    cerebro_bmrk.adddata(bt.feeds.PandasData(dataname=candles), name=symbol)
    cerebro_bmrk.addstrategy(strategy)
    cerebro_bmrk.addsizer(bt.sizers.PercentSizer, percents=bet_pct)
    cerebro_bmrk.run()
    bmrk_final_value = cerebro_bmrk.broker.getvalue()
    bmrk_pct_return = calculate_pct_return(cerebro_bmrk, cash)
    return bmrk_final_value, bmrk_pct_return
