#region imports
from AlgorithmImports import *
#endregion
class FailureTrader(QCAlgorithm):

    def Initialize(self):
        
        #focus on ES
        continuous_future_symbol = []
        continuous_future_symbol.append(Symbol.Create(Futures.Indices.SP500EMini, SecurityType.Future, Market.CME))
        continuous_future_symbol.append(Symbol.Create(Futures.Indices.SP500EMicro, SecurityType.Future, Market.CME))
        contract_symbols = self.FutureChainProvider.GetFutureContractList(continuous_future_symbol, self.Time)
        self.contract_symbol = sorted(contract_symbols, key=lambda symbol: symbol.ID.Date)[0]

        
        self.entryTicket = None
        self.stopMarketTicket = None
        self.entryTime = datetime.min
        self.stopMarketOrderFillTime = datetime.min
    
    def OnData(self, data):

        #Wait 15 minutes after last exit
        if (self.Time - self.stopMarketOrderFillTime).minutes < 15:
            return

        # send entry limit order
        # need to generate a different buy signal from a failure detection
        if not self.Portfolio.Invested and not self.Transactions.GetOpenOrders(self.qqq):
            quantity = self.CalculateOrderQuantity(self.qqq, 0.9) #update this to 1% of portfolio or 1 micro contract
            self.entryTicket = self.LimitOrder(self.qqq, quantity, price, "Entry Order")
            self.entryTime = self.Time
        
        # always need to have a stop in. This is a trailing stop
        # 5 pt trailing stop
        if self.stopMarketTicket is not None and self.Portfolio.Invested:
            # move up trailing stop price
            if price > self.highestPrice:
                self.highestPrice = price
                updateFields = UpdateOrderFields()
                updateFields.StopPrice = price - 5
                self.stopMarketTicket.Update(updateFields)
                #self.Debug(updateFields.StopPrice)
    
    def OnOrderEvent(self, orderEvent):
        
        if orderEvent.Status != OrderStatus.Filled:
            return
        
        # send stop loss order if entry limit order is filled
        if self.entryTicket is not None and self.entryTicket.OrderId == orderEvent.OrderId:
            self.stopMarketTicket = self.StopMarketOrder(self.qqq, -self.entryTicket.Quantity, 0.95 * self.entryTicket.AverageFillPrice)
        
        # save fill time of stop loss order (and reset highestPrice)
        if self.stopMarketTicket is not None and self.stopMarketTicket.OrderId == orderEvent.OrderId: 
            self.stopMarketOrderFillTime = self.Time
            self.highestPrice = 0