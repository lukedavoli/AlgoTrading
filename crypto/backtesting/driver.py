import json
import argparse

import utilities
from strategies import BuyAndHold, SMACrossover
from analysers import TotalCommission
from backtrader import bt

PCT_99 = 99

if __name__ == '__main__':
    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("config", action="store")  # configuration file
    parser.add_argument("-b", "--benchmark", action="store_true")  # benchmark
    parser.add_argument("-p", "--plot", action="store_true")  # plot
    args = parser.parse_args()

    # read configuration options from JSON file
    with open(args.config, 'r') as j:
        config = json.loads(j.read())
    CASH = config['cash']
    COMMISSION = config['commission']
    STRATEGY = config['strategy']

    # get the candles for all chosen markets
    market_candles = []
    markets_list = config['markets']
    for market in markets_list:
        market_candles.append(utilities.get_candles(market, config['dates']['start'], config['dates']['end']))

    if args.benchmark:
        # run the buy and hold strategy to set a benchmark for the strategy
        print("Getting benchmark with 'Buy and Hold' strategy...")
        bmrk_finalval, bmrk_pctreturn = utilities.get_benchmark(
            BuyAndHold, market_candles, markets_list, CASH, COMMISSION
        )

    # run the strategy with each pair of parameters and collect necessary information
    results = []
    param_sets = config['parameters']
    # repeat the process with each set of parameters from the options file
    for param_set in param_sets:
        cerebro_smax = bt.Cerebro()
        cerebro_smax.broker.setcash(CASH)
        cerebro_smax.addsizer(bt.sizers.PercentSizer, percents=PCT_99/len(market_candles))
        cerebro_smax.broker.setcommission(commission=COMMISSION)
        for i, market in enumerate(market_candles):
            cerebro_smax.adddata(bt.feeds.PandasData(dataname=market), name=markets_list[i])
        if STRATEGY == 'SMACrossover':
            cerebro_smax.addstrategy(
                SMACrossover, 
                sma_fast=param_set['fast'], sma_slow=param_set['slow'],
                crossover_margin=param_set['crossover_margin']
            )
            print('\nBacktesting SMA Crossover: fast-{}, slow-{}, margin-{}...'.format(
                param_set['fast'], param_set['slow'], param_set['crossover_margin']
            ))
        elif STRATEGY == 'RSIResponse':
            pass # example of another strategy
        else:
            print("Invalid strategy")
            raise ValueError
        cerebro_smax.addanalyzer(TotalCommission, _name='totalcomm')
        
        strat = cerebro_smax.run()[0]
        if args.plot:
            cerebro_smax.plot()

        # collect results
        param_set['final_portfolio_value'] = cerebro_smax.broker.getvalue()
        param_set['pct_return'] = utilities.calculate_pct_return(cerebro_smax, CASH)
        if args.benchmark:
            param_set['net_vs_benchmark'] = param_set['final_portfolio_value'] - bmrk_finalval
            param_set['alpha'] = param_set['pct_return'] - bmrk_pctreturn
        param_set['commission_costs'] = strat.analyzers.totalcomm.get_analysis()
        results.append(param_set)
        
    print("\n----------------RESULTS----------------\n")
    if args.benchmark:
        print("Buy and Hold (Benchmark)\nFinal Value: {}\nPercent Return: {}\n".format(
            bmrk_finalval, bmrk_pctreturn
        ))
    print("{} strategy results".format(STRATEGY))
    print(json.dumps(results, indent=4))
