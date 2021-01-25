import alpaca_backtrader_api
import backtrader as bt
import algo
import logger
import pandas as pd
import logger
from datetime import datetime

BACKTRADER = True
START_DATE = datetime(2016,3,21) # year, month, day
END_DATE = datetime(2016,4,10)	

class DavidStrat(bt.Strategy):
	params = (('security', None),)
	def __init__(self):
		self.security = self.params.security
		self.orefs = list()

	def notify_order(self, order):
		if not order.alive() and order.ref in self.orefs:
			self.orefs.remove(order.ref)

	def next(self):
		if len(self.orefs) > 0:
			return  # pending orders do nothing

		data_size = len(self.data.close)
		if data_size < 50:
			return
		
		prices = []
		for i in range(100):
			prices.append([
				self.data.open[-i], 
				self.data.high[-i], 
				self.data.low[-i], 
				self.data.close[-i], 
				self.data.volume[-i], 
				self.data.openinterest[-i]])

		global data_frame
		data_frame = pd.DataFrame(prices, columns = ['open','high','low','close','volume','openinterest'], dtype=float) # index = ['timestamp']
		
		# order = algo.buy_and_sell_david_custom(self.security, self)
		order = algo.buy_or_sell_macd_rsi(self.security, self)

		if order is not None:
			self.orefs = [o.ref for o in order]

def run(security):
	# grabbing our data from specified time periods (API HTTPS call)
	DataFactory = alpaca_backtrader_api.AlpacaData
	data = DataFactory(
		dataname=security.ticker,
		timeframe=bt.TimeFrame.Minutes,
		fromdate=START_DATE,
		todate=END_DATE,
		historical=True)

	# adding strat + data
	cerebro = bt.Cerebro()
	cerebro.broker.setcash(10000)
	# cerebro.broker.setcommission(commission=0.0)
	cerebro.addstrategy(DavidStrat, security=security)
	cerebro.adddata(data)

	logger.logp('running - starting portfolio value: %.2f' % cerebro.broker.getvalue())
	cerebro.run()
	logger.logp('final portfolio value: %.2f' % cerebro.broker.getvalue())
	cerebro.plot()