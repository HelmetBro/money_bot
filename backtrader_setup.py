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
			return 

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
		global strategy
		strategy = self
		
		order = algo.buy_and_sell_david_custom(security)
		logger.log(order)
		if order is not None:
			self.orefs = [o.ref for o in order]

# order = process_api.api.submit_order(
# 			symbol=self.ticker,
# 			side='buy',
# 			type='limit',
# 			qty=self.max_buy_qty(), ###later need to consider updating allowance when a sell order executes
# 			limit_price=str(self.current_price()+0.01),
# 			time_in_force='gtc',
# 			order_class='bracket',
# 			take_profit={'limit_price': upper_bound},
# 			stop_loss={'stop_price': lower_bound})

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