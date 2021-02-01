import json
import optparse

from utilities import cerebro_setup, get_candles, calculate_pct_return
from strategies import BuyAndHold, SMACrossover
from analysers import TotalCommission

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
    cerebro_bah = cerebro_setup(df_candles, betsizerpercent=99.6)
    cerebro_bah.addstrategy(BuyAndHold)
    print("Backtesting buy and hold strategy...")
    cerebro_bah.run()
    bah_final_value = cerebro_bah.broker.getvalue()
    bah_pct_return = calculate_pct_return(cerebro_bah, CASH)

    # define parameters for strategy
    param_sets = [
        dict(fast=50, slow=1000),
        dict(fast=200, slow=1000),
    ]

    # run the strategy with each pair of parameters and collect necessary information
    results = []
    for param_set in param_sets:
        cerebro_smax = cerebro_setup(df_candles)
        cerebro_smax.addstrategy(SMACrossover, sma_fast=param_set['fast'], sma_slow=param_set['slow'])
        cerebro_smax.addanalyzer(TotalCommission, _name='totalcomm')
        print('\nBacktesting SMA Crossover Strategy with short MA {} and long MA {}...'.format(
            param_set['fast'], param_set['slow']
        ))
        strat = cerebro_smax.run()[0]

        param_set['final_portfolio_value'] = cerebro_smax.broker.getvalue()
        param_set['pct_return'] = calculate_pct_return(cerebro_smax, CASH)
        param_set['net_vs_benchmark'] = param_set['final_portfolio_value'] - bah_final_value
        param_set['alpha'] = param_set['pct_return'] - bah_pct_return
        param_set['commission_costs'] = strat.analyzers.totalcomm.get_analysis()
        results.append(param_set)

    print("\n----------------RESULTS----------------")
    print(json.dumps(results, indent=4))
