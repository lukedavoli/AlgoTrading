import json
import optparse

from utilities import cerebro_setup, get_candles, calculate_pct_return
from strategies import BuyAndHold, SMACrossover

CASH = 10000

if __name__ == '__main__':
    # parse command line options
    parser = optparse.OptionParser()
    parser.add_option(
        '-c', '--candles',
        action="store", dest="candles",
        help="query string", default="existing"
    )
    options, args = parser.parse_args()

    # either update the candles from the database or use the existing ones from file
    df_candles = get_candles(options.candles)

    # run the buy and hold strategy to set a benchmark for the strategy
    cerebro_bah = cerebro_setup(df_candles, BuyAndHold, betsizerpercent=99.6, cash=CASH)
    print("Backtesting buy and hold strategy...")
    cerebro_bah.run()
    bah_pct_return = calculate_pct_return(cerebro_bah, CASH)

    # define parameters for strategy
    strategies = [
        dict(short=50, long=1000),
        dict(short=200, long=1000),
        dict(short=200, long=2000),
        dict(short=200, long=4000),
        dict(short=500, long=1000),
        dict(short=500, long=5000),
        dict(short=500, long=10000),
    ]

    # run the strategy with each pair of parameters and collect necessary information
    results = []
    for strat in strategies:
        cerebro_smax = cerebro_setup(
            df_candles, SMACrossover,
            sma_short_length=strat['short'], sma_long_length=strat['long']
        )
        print('\nBacktesting SMA Crossover Strategy with short MA {} and long MA {}...'.format(
            strat['short'], strat['long']
        ))
        cerebro_smax.run()

        strat['final_val'] = cerebro_smax.broker.getvalue()
        strat['pct_return'] = calculate_pct_return(cerebro_smax, CASH)
        strat['alpha'] = strat['pct_return'] - bah_pct_return
        results.append(strat)

    print("\n----------------RESULTS----------------")
    print(json.dumps(results, indent=4))
