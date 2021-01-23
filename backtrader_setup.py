import alpaca_backtrader_api
import backtrader as bt
import algo
import logger
import pandas as pd
import logger
from datetime import datetime

BACKTRADER = True

class DavidStrat(bt.Strategy):
	def __init__(self):
		self.orefs = list()

	def notify_order(self, order):
		if not order.alive() and order.ref in self.orefs:
			self.orefs.remove(order.ref)

	def next(self):
		if self.orefs:
			return  # pending orders do nothing
		if self.position:
			return # current positions don't submit orders

		data_size = len(self.data.close)
		if data_size < 50:
			return
		
		prices = []
		for i in range(data_size):
			prices.append([
				self.data.open[-i], 
				self.data.high[-i], 
				self.data.low[-i], 
				self.data.close[-i], 
				self.data.volume[-i], 
				self.data.close[-i]]) #vwap

		global data_frame
		data_frame = pd.DataFrame(prices, columns = ['open','high','low','close','volume','vwap'], dtype=float) # index = ['timestamp']
		
		order = algo.buy_and_sell_david_custom(security, self)
		if order is not None:
			self.orefs = [o.ref for o in order]

def run(sec):
	global security
	security = sec

	START_DATE = datetime(2020,8,5)
	END_DATE = datetime(2020,8,10)	

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
	cerebro.broker.setcash(100000)
	cerebro.broker.setcommission(commission=0.0)
	cerebro.addstrategy(DavidStrat)
	cerebro.adddata(data)

	logger.logp('running - starting portfolio value: %.2f' % cerebro.broker.getvalue())
	cerebro.run()
	logger.logp('final portfolio value: %.2f' % cerebro.broker.getvalue())
    # cerebro.plot()