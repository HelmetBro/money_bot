from func_timeout import func_set_timeout

import logger

TIMEOUT = 9

# to be run in a thread by the main process
def listen(pipe):
	import alpaca_backtrader_api as trader_api
	api = trader_api.REST()

	while True:
		# listen to pipe, and submit requests accordingly
		transaction = pipe.recv()
		order = transaction.submit(api)
		pipe.send(order)

class transaction:
	order_pipe = None

	ticker = None
	side = None
	type = None
	qty = None
	time_in_force = None

	def __init__(self, order_pipe, ticker, side, type, qty, time_in_force):
		self.order_pipe = order_pipe
		self.ticker = ticker
		self.side = side
		self.type = type
		self.qty = qty
		self.time_in_force = time_in_force

		# cancel all current orders

		# if backtrader_setup.BACKTRADER:
		# 	if trader is None:
		# 		raise Exception("trader cannot be None when backtrading!")
		# 	if trader.position:
		# 		return # current positions don't submit buy orders
		# 	logger.logp("submitted buy order for {} at {}!".format(self.ticker, backtrader_setup.data_frame['close'][0]))
		# 	return trader.buy(
		# 		size=int(trader.broker.get_cash() / backtrader_setup.data_frame['close'][0]))
		# 	# return trader.buy(
		# 	#     price=backtrader_setup.data_frame['open'][0],
		# 	#     exectype=backtrader.Order.Limit)

		# if self.has_position():
		# 	logger.log("position already exists with {} shares!".format(self.position.qty), 'debug')
		# 	return
	
	# only to be called by main processes sub-thread, listen()
	def submit(self, api):
		order = api.submit_order(
			symbol=self.ticker,
			side=self.side,
			type=self.type,
			qty=self.qty,
			time_in_force=self.time_in_force)
		logger.logp(self.get_info())
		return order
	
	def get_info(self):
		return "submitted order: {}, qty {}, side {}, type {}, tif {}".format(
			self.ticker,
			self.qty,
			self.side,
			self.type,
			self.time_in_force)

def market_buy(order_pipe, ticker, qty):
	t = transaction(order_pipe, ticker, 'buy', 'market', qty, 'fok')
	order_pipe.send(t)
	return order_pipe.recv()

def market_sell(order_pipe, ticker, qty):
	t = transaction(order_pipe, ticker, 'sell', 'market', qty, 'fok')
	order_pipe.send(t)
	return order_pipe.recv()