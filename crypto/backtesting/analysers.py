from backtrader import Analyzer

class TotalCommission(Analyzer):
    def __init__(self):
        self.commission_spent = 0
    
    def notify_order(self, order):
        self.commission_spent += order.executed.comm

    def get_analysis(self):
        return self.commission_spent