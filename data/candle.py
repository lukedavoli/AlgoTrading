import datetime

class Candle:
    def __init__(self, *, market=None, btrx_dict=None, db_tuple=None):
        if market and btrx_dict:
            self.market = market
            self.date_time = datetime.datetime.strptime(btrx_dict['startsAt'], '%Y-%m-%dT%H:%M:%SZ')
            self.open_ = btrx_dict['open']
            self.high = btrx_dict['high']
            self.low = btrx_dict['low']
            self.close = btrx_dict['close']
            self.quote_volume = btrx_dict['quoteVolume']
        elif db_tuple:
            self.market = db_tuple[0]
            self.date_time = datetime.datetime.strptime(db_tuple[1], '%Y-%m-%d %H:%M:%S')
            self.open_ = db_tuple[2]
            self.high = db_tuple[3]
            self.low = db_tuple[4]
            self.close = db_tuple[5]
            self.quote_volume = db_tuple[6]
        else:
            raise ValueError("arguments 'market' and 'btrx_dict' must be provided together or argument 'db_tuple'"
                             "alone, all arguments must be explicitly named.")

    def __repr__(self):
        return "Candle({}|{})".format(self.market, self.date_time)

