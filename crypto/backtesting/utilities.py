import backtrader as bt
import pandas as pd
import sys
import os

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from dao import Dao


def cerebro_setup(
    data, strategy, cash=10000, betsizerpercent=20, commission=0.004,
    sma_short_length=None, sma_long_length=None
):

    cerebro = bt.Cerebro()
    cerebro.adddata(bt.feeds.PandasData(dataname=data))
    cerebro.broker.setcash(cash)
    cerebro.addsizer(bt.sizers.PercentSizer, percents=betsizerpercent)
    cerebro.broker.setcommission(commission=commission)
    if sma_short_length and sma_long_length:
        cerebro.addstrategy(
            strategy, sma_short_length=sma_short_length, sma_long_length=sma_long_length
        )
    else:
        cerebro.addstrategy(strategy)
    return cerebro


def get_candles(source):
    df_candles = None
    if source == 'new':
        db = Dao()
        candles = db.get_candles(market='EOS-USDT')
        df_candles = pd.DataFrame(candles, columns=[
            'market', 'date_time', 'open', 'high', 'low', 'close', 'volume'
        ])
        df_candles.drop(columns='market', inplace=True)
        df_candles['date_time'] = pd.to_datetime(df_candles['date_time'])
        df_candles.set_index('date_time', inplace=True)
        df_candles.to_csv('candles.csv')
    elif source == 'existing':
        df_candles = pd.read_csv('candles.csv', index_col='date_time', parse_dates=True)
    return df_candles


def calculate_pct_return(cerebro, cash):
    return ((cerebro.broker.getvalue() - cash) / cash) * 100
