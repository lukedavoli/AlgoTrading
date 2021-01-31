import os
import sys
import json
import optparse
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import backtrader as bt

from strat_sma_crossover import SMACrossover

sys.path.insert(1, os.path.join(sys.path[0], '..'))
from dao import Dao

if __name__ == '__main__':
    parser = optparse.OptionParser()
    parser.add_option('-c', '--candles',
        action="store", dest="candles",
        help="query string", default="existing")
    options, args = parser.parse_args()

    # depending on the command line option chosen, either update the candles from the database or use the existing ones
    df_candles = None
    if options.candles == 'new':
        db = Dao()
        candles = db.get_candles(market='EOS-USDT')
        df_candles = pd.DataFrame(candles, columns=['market', 'date_time', 'open', 'high', 'low', 'close', 'volume'])
        df_candles.drop(columns='market', inplace=True)
        df_candles['date_time'] = pd.to_datetime(df_candles['date_time'])
        df_candles.set_index('date_time', inplace=True)
        df_candles.to_csv('candles.csv')
    elif options.candles == 'existing':
        df_candles = pd.read_csv('candles.csv', index_col='date_time', parse_dates=True)

    strategies = [
        dict(short=50, long=1000),
    ]

    results = []
    for strat in strategies:
        cerebro = bt.Cerebro()
        cerebro.adddata(bt.feeds.PandasData(dataname=df_candles))
        cerebro.broker.setcash(10000.0)
        cerebro.addsizer(bt.sizers.PercentSizer, percents=20)
        cerebro.broker.setcommission(commission=0.004)
        cerebro.addstrategy(SMACrossover, sma_short_length=strat['short'], sma_long_length=strat['long'])

        print('\nBacktesting SMA Crossover Strategy with short MA {} and long MA {}...'.format(strat['short'], strat['long']))
        print('Start Portfolio Value: %.2f' % cerebro.broker.getvalue())
        cerebro.run()
        print('Final Portfolio Value: %.2f' % cerebro.broker.getvalue())

        strat['final_val'] = cerebro.broker.getvalue()
        results.append(strat)

    print("\n----------------RESULTS----------------")
    print(json.dumps(results, indent=4))


    




