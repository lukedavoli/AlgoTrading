import json
import argparse

import utilities
from strategies import BuyAndHold, SMACrossover, XHold
from analysers import TotalCommission
from backtrader import bt

PCT_99 = 99.6

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
    COMMISSION = config['commission']/100
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
    parameters_results = []
    param_sets = config['parameters']
    # repeat the process with each set of parameters from the options file
    for param_set in param_sets:
        markets_results = []
        for i, market in enumerate(market_candles):
            # set up simulator with cash, betsizer, commission, data for markets
            cerebro_smax = bt.Cerebro()
            cerebro_smax.broker.setcash(CASH)
            cerebro_smax.addsizer(bt.sizers.PercentSizer, percents=PCT_99)
            cerebro_smax.broker.setcommission(commission=COMMISSION)
            cerebro_smax.adddata(bt.feeds.PandasData(dataname=market), name=markets_list[i])
            
            # add a stratgey
            if STRATEGY == 'SMACrossover':
                cerebro_smax.addstrategy(
                    SMACrossover, 
                    sma_fast=param_set['fast'], sma_slow=param_set['slow'],
                    crossover_margin=param_set['crossover_margin']
                )
                print('\nSMA Crossover: market-{} fast-{}, slow-{}, margin-{}...'.format(
                    markets_list[i], param_set['fast'], param_set['slow'], param_set['crossover_margin']
                ))
            elif STRATEGY == 'XHold':
                cerebro_smax.addstrategy(
                    XHold, ema_fast=param_set['ema_fast'], ema_slow=param_set['ema_slow'],
                    pmt=param_set['pmt'], prt=param_set['prt'], brpsp=param_set['brpsp'],
                    crossover_margin=param_set['crossover_margin']
                )
                print('\nCrossover and Hold ({}):, ema_fast-{}, ema_slow-{}, pmt-{}, prt-{}, brpsp-{}...'.format(
                    markets_list[i], param_set['ema_fast'], param_set['ema_slow'], param_set['pmt'], param_set['prt'], param_set['brpsp']
                ))
            else:
                print("Invalid strategy")
                raise ValueError
            cerebro_smax.addanalyzer(TotalCommission, _name='totalcomm')
            
            strat = cerebro_smax.run()[0]
            if args.plot:
                cerebro_smax.plot()

            # collect results for this market with this set of parameters
            mrkt_results = {}
            mrkt_results['final_portfolio_value'] = cerebro_smax.broker.getvalue()
            mrkt_results['pct_return'] = utilities.calculate_pct_return(cerebro_smax, CASH)
            if args.benchmark:
                mrkt_results['net_vs_benchmark'] = mrkt_results['final_portfolio_value'] - bmrk_finalval
                mrkt_results['alpha'] = mrkt_results['pct_return'] - bmrk_pctreturn
            mrkt_results['commission_costs'] = strat.analyzers.totalcomm.get_analysis()
            markets_results.append(mrkt_results)
        # Average the results for the markets in this parameter setup
        param_results = {}
        param_results['params'] = param_set
        for key in markets_results[0].keys():
            param_results[key] = sum(d[key] for d in markets_results) / len(markets_results)
        parameters_results.append(param_results)

        
    print("\n----------------RESULTS----------------\n")
    if args.benchmark:
        print("Buy and Hold (Benchmark)\nFinal Value: {}\nPercent Return: {}\n".format(
            bmrk_finalval, bmrk_pctreturn
        ))
    print("{} strategy results".format(STRATEGY))
    print(json.dumps(parameters_results, indent=4))
