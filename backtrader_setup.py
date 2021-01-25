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
		self.open_orders = list()

	def notify_order(self, order):
		if order.status in [order.Submitted, order.Accepted]:
			# buy/sell order submitted/accepted to/by broker - nothing to do
			return

		# Check if an order has been completed
		# Attention: broker could reject order if not enough cash
		if order.status in [order.Completed]:
			if order.isbuy():
				logger.logp('BUY EXECUTED, %.2f' % order.executed.price)
			elif order.issell():
				self.security.allowance = order.executed.price * order.executed.size
				logger.logp('SELL EXECUTED, %.2f' % order.executed.price)

		elif order.status in [order.Canceled, order.Margin, order.Rejected]:
			logger.logp('order canceled/margin/rejected')

		if not order.alive() and order.ref in self.open_orders:
			self.open_orders.remove(order.ref)

	def next(self):
		if len(self.open_orders) > 0:
			print(self.open_orders[0])
			print("skipped :(")
			return

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
		
		order = algo.buy_and_sell_david_custom(self.security, self)
		# order = algo.buy_or_sell_macd_rsi(self.security, self)

		if order is not None:
			if isinstance(order, list):
				self.open_orders = [o.ref for o in order]
			else:
				self.open_orders.append(order.ref)

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

	before_value = cerebro.broker.getvalue()
	logger.logp('running - starting portfolio value: %.2f' % before_value)
	cerebro.run()

	after_value = cerebro.broker.getvalue()
	logger.logp('final portfolio value: %.2f' % after_value)
	logger.logp('profit: $%.2f' % float(after_value - before_value))
	cerebro.plot()