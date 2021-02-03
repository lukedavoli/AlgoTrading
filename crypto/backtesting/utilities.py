import backtrader as bt
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from dao import Dao

PCT_99 = 99

def get_candles(market, start_date, end_date):
    df_candles = None
    try:
        df_candles = pd.read_csv(
            'candles/{}.csv'.format(market), index_col='date_time', parse_dates=True
        )
    except FileNotFoundError:
        db = Dao()
        candles = db.get_candles(market=market)
        df_candles = pd.DataFrame(candles, columns=[
            'market', 'date_time', 'open', 'high', 'low', 'close', 'volume'
        ])
        df_candles.drop(columns='market', inplace=True)
        df_candles['date_time'] = pd.to_datetime(df_candles['date_time'])
        df_candles.set_index('date_time', inplace=True)
        df_candles.to_csv('candles/{}.csv'.format(market))
    if start_date:
        start_dt = datetime.strptime(start_date, '%Y-%m-%d')
        df_candles = df_candles[df_candles.index >= start_dt]
    if end_date:
        end_dt = datetime.strptime(end_date, '%Y-%m-%d')
        df_candles = df_candles[df_candles.index <= end_dt]
    return df_candles


def calculate_pct_return(cerebro, cash):
    return ((cerebro.broker.getvalue() - cash) / cash) * 100


def get_benchmark(strategy, markets, markets_list, cash, commission):
    cerebro_bmrk = bt.Cerebro()
    cerebro_bmrk.broker.setcash(cash)
    buy_spend = (cash - 100) / len(markets)
    cerebro_bmrk.broker.setcommission(commission=commission)
    for i, market in enumerate(markets):
        cerebro_bmrk.adddata(bt.feeds.PandasData(dataname=market), name=markets_list[i])
    cerebro_bmrk.addstrategy(strategy, buy_spend=buy_spend)
    cerebro_bmrk.run()
    cerebro_bmrk.plot()
    bmrk_final_value = cerebro_bmrk.broker.getvalue()
    bmrk_pct_return = calculate_pct_return(cerebro_bmrk, cash)
    return bmrk_final_value, bmrk_pct_return
