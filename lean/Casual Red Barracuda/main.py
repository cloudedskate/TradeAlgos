# region imports
from AlgorithmImports import *
# endregion

class CasualRedBarracuda(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2021, 4, 23)  # Set Start Date
        self.SetEndDate(2022, 10, 1)
        self.SetCash(100000)  # Set Strategy Cash
        self.spy = self.AddEquity("SPY",Resolution.Daily).Symbol

        self.sma = self.SMA(self.spy, 30, Resolution.Daily)
        closing_prices = self.History(self.spy, 30, Resolution.Daily)["close"]
        for time, price in closing_prices.loc[self.spy].items():
            self.sma.Update(time,price)
        




    def OnData(self, data: Slice):
        if not self.sma.IsReady:
            return
        
        hist = self.History(self.spy, timedelta(365), Resolution.Daily)
        low = min(hist["low"])
        high = max(hist["high"])

        price = self.Securities[self.spy].Price

        if price * 1.05 >= high and self.sma.Current.Value < price:
            if not self.Portfolio(self.spy).IsLong:
                self.SetHoldings(self.spy, 1)
        
        elif price * .95 >= low and self.sma.Current.Value > price:
            if not self.Portfolio(self.spy).IsShort:
                self.SetHoldings(self.spy, -1)
        
        else:
            self.Liquidate()

        self.Plot("Benchmark, 52w-High", high)
        self.Plot("Benchmark, 52w-Low", low)
        self.Plot("Benchmark, SMA", self.sma.Current.Value)


        
