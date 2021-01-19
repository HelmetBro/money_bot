import alpaca_backtrader_api
import backtrader as bt
import algo
import logger
import time
import numpy as np
import pandas as pd
from datetime import datetime


START_DATE = datetime(2017, 1, 1)
END_DATE = datetime(2017, 1, 2)

class SmaCross(bt.SignalStrategy):
	def __init__(self):
		# end = self.data.datetime.date()
		# start = end - datetime.timedelta(hours=1)
		sma1, sma2 = bt.ind.SMA(period=10), bt.ind.SMA(period=30)
		crossover = bt.ind.CrossOver(sma1, sma2)
		self.signal_add(bt.SIGNAL_LONG, crossover)

class DavidStrat(bt.Strategy):
	def __init__(self):
		# six columns emulating response from Alpaca API
		data_frame = pd.DataFrame([[None] * 6], columns = ['open','high','low','close','volume','vwap']) # index = ['timestamp']
		print('test0')
		self.dataclose = self.datas[0].close
		print('after')
		
	def next(self):
		print('test1')
		end = self.data.datetime.date() 
		start = end - datetime.timedelta(hours=1)

		print(self.dataclose[0])
		# print(self.data.close[-1])
		# print(self.data.close[-2])

		# decision,upper_bound,lower_bound = algo.buy_and_sell_david_custom(self.ticker, start, end, self.data)

        # if decision == 'buy_limit_stop':
        #     self.buy(
        #         exectype=Order.StopLimit
        #     )

# order = process_api.api.submit_order(
#             symbol=self.ticker,
#             side='buy',
#             type='limit',
#             qty=self.max_buy_qty(), ###later need to consider updating allowance when a sell order executes
#             limit_price=str(self.current_price()+0.01),
#             time_in_force='gtc',
#             order_class='bracket',
#             take_profit={'limit_price': upper_bound},
#             stop_loss={'stop_price': lower_bound})

def run(ticker):
	# grabbing our data from specified time periods (API HTTPS call)
	DataFactory = alpaca_backtrader_api.AlpacaData
	data = DataFactory(dataname=ticker,fromdate=START_DATE,todate=END_DATE, timeframe=bt.TimeFrame.Minutes)

    # adding strat + data
	cerebro = bt.Cerebro()
	cerebro.broker.setcash(10000.0)
	cerebro.addstrategy(DavidStrat)
	cerebro.adddata(data)

	logger.logp(ticker + ' starting Portfolio Value: %.2f' % cerebro.broker.getvalue())
	cerebro.run()
	logger.logp(ticker + ' final Portfolio Value: %.2f' % cerebro.broker.getvalue())
    # cerebro.plot()