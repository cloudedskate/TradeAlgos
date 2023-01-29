class ContinuousFutureRegressionAlgorithm(QCAlgorithm):
    def Initialize(self):
        '''Initialise the data and resolution required, as well as the cash and start-end dates for your algorithm. All algorithms must initialized.'''
        self.SetCash(1000000)
        self.SetStartDate(2019, 1, 1)
        self.SetEndDate(2021, 6, 1)

        self._lastDateLog = -1
        self._continuousContract = self.AddFuture(Futures.Energies.CrudeOilWTI,
                                                  dataNormalizationMode = DataNormalizationMode.BackwardsRatio,
                                                  dataMappingMode = DataMappingMode.OpenInterest,
                                                  contractDepthOffset = 0)
        self.Schedule.On(self.DateRules.EveryDay(), self.TimeRules.Midnight, self.PlotPrices);

    def PlotPrices(self):
        if self._continuousContract.HasData:
            self.Plot(self._continuousContract.Symbol.ID.Symbol, self._continuousContract.Symbol.ID.Symbol, self._continuousContract.Price)

    def OnData(self, data):
        '''OnData event is the primary entry point for your algorithm. Each new data point will be pumped in here.
        Arguments:
            data: Slice object keyed by symbol containing the stock data
        '''
        for changedEvent in data.SymbolChangedEvents.Values:
            if changedEvent.Symbol == self._continuousContract.Symbol:
                self.Log(f"SymbolChanged event: {changedEvent}")

        if not self.Portfolio.Invested:
            self.Buy(self._continuousContract.Symbol, 1)

        if self._lastDateLog != self.Time.month:
            self._lastDateLog = self.Time.month
            response = self.History( [ self._continuousContract.Symbol ], 60 * 24 * 90)
            if response.empty:
                raise ValueError("Unexpected empty history response")

    def OnOrderEvent(self, orderEvent):
        if orderEvent.Status == OrderStatus.Filled:
            self.Debug("Purchased Stock: {0}".format(orderEvent.Symbol))
