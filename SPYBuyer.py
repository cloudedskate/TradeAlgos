# region imports
from AlgorithmImports import *
# endregion

class MeasuredFluorescentPinkCow(QCAlgorithm):

    def Initialize(self):
        self.SetStartDate(2021, 4, 22)  # Set Start Date
        self.SetEndDate(2022, 10, 1)
        self.SetCash(100000)  # Set Strategy Cash

        spy = self.AddEquity("SPY", Resolution.Daily)

        spy.SetDataNormalizationMode(DataNormalizationMode.Raw)

        self.spy = spy.Symbol

        self.SetBenchmark("SPY")
        self.SetBrokerageModel(BrokerageName.InteractiveBrokersBrokerage, AccountType.Margin)

        self.entryPrice = 0
        self.period = timedelta(31)
        self.nextEntryTime = self.Time




    def OnData(self, data):
        if not self.spy in data:
            return
                
        #price = self.data.Bars[self.spy].Close #close price of day before
        price = data[self.spy].Close
        #price = self.Securities(self.spy).Close

        #trade logic
        if not self.Portfolio.Invested:
            if self.nextEntryTime <= self.Time:
                self.SetHoldings(self.spy, 1) #invest 100% of portfolio in spy
                #self.MarketOrder(self.spy, int(self.Portfolio.Cash / price)) #marketorder into maximum number of shares
                self.Log("Buy SPY at " + str(price))
                self.entryPrice = price
        
        elif self.entryPrice * 1.1 < price or self.entryPrice * 0.9 > price:
            self.Liquidate()
            self.Log("Sell SPY at " + str(price))
            self.nextEntryTime = self.Time + self.period #stay in cash for next month

        pass

