import backtrader as bt


class BuyAndHold(bt.Strategy):
    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None

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
        self.order = None

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
        if self.order:  # If an order already exists...
            return  # ...then we cannot send another one, leave method
        if not self.position:  # If we are not in a position...
            self.log('BUY CREATE, %.2f' % self.dataclose[0])
            self.order = self.buy()


class SMACrossover(bt.Strategy):
    params = (('sma_fast', 12), ('sma_slow', 288),)

    def __init__(self):
        self.dataclose = self.datas[0].close
        self.order = None
        self.buyprice = None
        self.buycomm = None

        # Add a MovingAverageSimple indicator
        self.sma_fast = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.sma_fast
        )
        self.sma_slow = bt.indicators.SimpleMovingAverage(
            self.datas[0], period=self.params.sma_slow
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
        self.order = None

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
        if self.order:  # If an order already exists...
            return  # ...then we cannot send another one, leave method
        if not self.position:  # "If we are not in a position...
            if self.sma_fast > self.sma_slow * 1.03:  # ...and the short-term SMA is higher than the long-term SMA...
                # ...then create a buy order and store a reference to it
                self.log('BUY CREATE, %.2f' % self.dataclose[0])
                self.order = self.buy()
        else:  # If we are already in a position...
            if self.sma_fast < self.sma_slow * 0.97:  # ...and the short-term SMA is lower than the long-term SMA
                # ...then create a sell order and store a reference to it
                self.log('SELL CREATE, %.2f' % self.dataclose[0])
                self.order = self.sell()
