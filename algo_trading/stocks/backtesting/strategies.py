import backtrader as bt


class BuyAndHold(bt.Strategy):
    params = (('buy_spend', 0),)
     
    def __init__(self):
        self.markets = dict()
        for d in self.datas:
            dn = d._name
            self.markets[dn] = dict(close = d.close, order = None, buyprice = None, buycomm = None)
        self.buy_spend = self.params.buy_spend

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:  # If the order is only submitted or accepted...
            return  # ...then do nothing
        if order.status in [order.Completed]:  # If the order is completed...
            if order.isbuy():  # ...and the order was a buy order...
                # ...then log the details of it and store the buy price and commission values
                self.log('BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm: %.2f' % (
                    order.executed.price,
                    order.executed.value,
                    order.executed.comm
                ))
                self.buyprice = order.executed.price
                self.buycomm = order.executed.comm
            elif order.issell():  # ...and the order was a sell order
                # ...then log the details of it
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm: %.2f' % (
                    order.executed.price,
                    order.executed.value,
                    order.executed.comm
                ))
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            self.log('Order Canceled/Margin/Rejected')
        self.markets[order.info.addinfo['dn']]['order'] = None

    def notify_trade(self, trade):
        if not trade.isclosed:  # If our current trade has not yet closed...
            return  # ...then there is nothing to do
        # Otherwise report the details of the operation
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (trade.pnl, trade.pnlcomm))

    # Logging function for this strategy
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def next(self):
        for d in self.datas:
            dn = d._name
            if self.markets[dn]['order']:  # If an order already exists...
                return  # ...then we cannot send another one, leave method
            if not self.getposition(d):  # If we are not in a position...
                self.log('BUY CREATE, %s, %.2f' % (dn, self.markets[dn]['close'][0]))
                oinfo = dict(dn=dn)
                size = self.buy_spend / self.markets[dn]['close'][0]
                self.markets[dn]['order'] = self.buy(data=d, addinfo=oinfo, size=size)


class XHold(bt.Strategy):
    params = (
        ('ema_fast', None), ('ema_slow', None), 
        ('pmt', None), ('prt', None), ('brpsp', None),
        ('crossover_margin', None)
    )

    def __init__(self):
        self.markets = dict()
        for d in self.datas:
            dn = d._name
            self.markets[dn] = dict(
                close = d.close, order = None, buyprice = None, buycomm = None, peak=0, sell_ready=False,
                ema_fast = bt.indicators.ExponentialMovingAverage(d, period=self.params.ema_fast),
                ema_slow = bt.indicators.ExponentialMovingAverage(d, period=self.params.ema_slow),
            )

    def notify_order(self, order):
        if order.status in [order.Submitted, order.Accepted]:  # If the order is only submitted or accepted...
            return  # ...then do nothing
        if order.status in [order.Completed]:  # If the order is completed...
            if order.isbuy():  # ...and the order was a buy order...
                # ...then log the details of it and store the buy price and commission values
                self.log('BUY EXECUTED, Price: %.2f, Cost: %.2f, Comm: %.2f' % (
                    order.executed.price,
                    order.executed.value,
                    order.executed.comm
                ))
                self.markets[order.info.addinfo['dn']]['buy_price'] = order.executed.price
                self.markets[order.info.addinfo['dn']]['buy_comm'] = order.executed.comm
            elif order.issell():  # ...and the order was a sell order
                # ...then log the details of it
                self.log('SELL EXECUTED, Price: %.2f, Cost: %.2f, Comm: %.2f' % (
                    order.executed.price,
                    order.executed.value,
                    order.executed.comm
                ))
            self.bar_executed = len(self)
        elif order.status in [order.Canceled, order.Margin, order.Rejected]:
            # self.log('Order Canceled/Margin/Rejected')
            pass
        self.markets[order.info.addinfo['dn']]['order'] = None

    def notify_trade(self, trade):
        if not trade.isclosed:  # If our current trade has not yet closed...
            return  # ...then there is nothing to do
        # Otherwise report the details of the operation
        self.log('OPERATION PROFIT, GROSS %.2f, NET %.2f' % (trade.pnl, trade.pnlcomm))

    # Logging function for this strategy
    def log(self, txt, dt=None):
        dt = dt or self.datas[0].datetime.date(0)
        print('%s, %s' % (dt.isoformat(), txt))

    def next(self):
        for d in self.datas:
            dn = d._name
            if self.markets[dn]['order']:  # If an order already exists...
                return  # ...then we cannot send another one, leave method
            if not self.getposition(d):  # "If we are not in a position...
                if self.markets[dn]['ema_fast'] > self.markets[dn]['ema_slow'] * (1 + self.params.crossover_margin/100):  # ...and the short-term EMA is higher than the long-term SMA...
                    # ...then create a buy order and store a reference to it
                    self.log('BUY CREATE, %s, %.2f' % (dn, self.markets[dn]['close'][0]))
                    oinfo = dict(dn=dn)
                    self.markets[dn]['order'] = self.buy(data=d, addinfo=oinfo)
                pass
            else:  # If we are already in a position...
                # if the close falls below our panic sell trigger, sell
                if self.markets[dn]['close'][0] < self.markets[dn]['buy_price'] * (1 - self.params.brpsp/100):
                    self.log('SELL CREATE, %s, %.2f' % (dn, self.markets[dn]['close'][0]))
                    oinfo = dict(dn=dn)
                    self.markets[dn]['order'] = self.sell(data=d, addinfo=oinfo)
                    # Reset variables
                    self.markets[dn]['peak'] = 0
                    self.markets[dn]['sell_ready'] = False
                # update the peak close price since we bought the market
                if self.markets[dn]['close'][0] > self.markets[dn]['peak']:
                    self.markets[dn]['peak'] = self.markets[dn]['close'][0]
                # if the peak is greater than what we paid plus x percent, we are ready to sell 
                if self.markets[dn]['peak'] >= self.markets[dn]['buy_price'] * (1 + self.params.pmt/100):
                    self.markets[dn]['sell_ready'] = True
                # if we are ready to sell and the close has retraced x percent of the current peak since buying, sell
                profit = self.markets[dn]['peak'] - self.markets[dn]['buy_price']
                retrace = self.markets[dn]['peak'] - self.markets[dn]['close'][0]
                if self.markets[dn]['sell_ready'] and retrace > profit * (self.params.prt/100):
                    # ...then create a sell order and store a reference to it
                    self.log('SELL CREATE, %s, %.2f' % (dn, self.markets[dn]['close'][0]))
                    oinfo = dict(dn=dn)
                    self.markets[dn]['order'] = self.sell(data=d, addinfo=oinfo)
                    # Reset variables
                    self.markets[dn]['peak'] = 0
                    self.markets[dn]['sell_ready'] = False