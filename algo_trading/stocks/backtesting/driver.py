import argparse
import logging
import json

import utilities
from strategies import BuyAndHold, XHold
from backtrader import bt

PCT_99 = 99
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    # parse command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("config", action="store")  # configuration file
    parser.add_argument("-b", "--benchmark", action="store_true")  # benchmark
    parser.add_argument("-p", "--plot", action="store_true")  # plot
    args = parser.parse_args()

    # read configuration options from JSON file
    logging.info("reading configuration file")
    with open(args.config, 'r') as j:
        config = json.loads(j.read())
    CASH = config['cash']
    COMMISSION = config['commission']
    STRATEGY = config['strategy']
    EXCHANGE = config['exchange']
    SYMBOL = config['symbol']
    START_DATE = config['dates']['start']
    END_DATE = config['dates']['end']
    PARAMS = config['parameters']

    # get the candles for the desired symbol
    candles = utilities.get_candles(EXCHANGE, SYMBOL, START_DATE, END_DATE)

    # get a benchmark if necessary
    if args.benchmark:
        logging.info("getting benchmark with 'Buy and Hold' strategy")
        bmrk_finalval, bmrk_pct_return = utilities.get_benchmark(
            BuyAndHold, candles, SYMBOL, CASH, COMMISSION/100, PCT_99
        )
    
    parameters_results = []
    for params in PARAMS:
        cerebro = bt.Cerebro()
        cerebro.broker.setcash(CASH)
        cerebro.broker.setcommission(commission=COMMISSION/100)
        cerebro.addsizer(bt.sizers.PercentSizer, percents=PCT_99)
        cerebro.adddata(bt.feeds.PandasData(dataname=candles), name=SYMBOL)
    
        if STRATEGY == 'XHold':
            cerebro.addstrategy(
                XHold, ema_fast=params['ema_fast'], ema_slow=params['ema_slow'],
                pmt=params['pmt'], prt=params['prt'], brpsp=params['brpsp'],
                crossover_margin=params['crossover_margin']
            )
            logging.info(
                "XHold Strategy: ema_fast({}), ema_slow({}), pmt({}), prt({}), brpsp({})".format(
                    params['ema_fast'], params['ema_slow'],
                    params['pmt'], params['prt'], params['brpsp'],
                )
            )
        else:
            logging.error("invalid strategy")
            raise ValueError

        cerebro.run()
        if args.plot:
            logging.info("plotting results")
            cerebro.plot()
        
        results = {}
        results['final_portfolio_value'] = cerebro.broker.getvalue()
        results['pct_return'] = utilities.calculate_pct_return(cerebro, CASH)
        if args.benchmark:
            results['net_vs_benchmark'] = results['final_portfolio_value'] - bmrk_finalval
            results['alpha'] = results['pct_return'] - bmrk_pctreturn
        parameters_results.append(results)

        print("\n----------------RESULTS----------------\n")
        if args.benchmark:
            print("Buy and Hold (Benchmark)\nFinal Value: {}\nPercent Return: {}\n".format(
                bmrk_finalval, bmrk_pctreturn
            ))
        print("{} strategy results".format(STRATEGY))
        print(json.dumps(parameters_results, indent=4))
        



        

    
