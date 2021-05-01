import logger

TIMEOUT = 9

# to be run in a thread by the main process
def listen(pipe):
	import alpaca_trade_api as trader_api
	api = trader_api.REST()

	while True:
		# listen to pipe, and submit requests accordingly
		transaction = pipe.recv()
		order = transaction.submit(api)
		pipe.send(order)

class transaction:
	# pipe where transaction is sent upstream
	order_pipe = None

	# basic values that may fill a transation
	time_in_force    = None
	ticker		     = None
	side 		     = None
	order_type       = None # market/limit/etc
	transaction_type = None # quantity or notional
	qty 	      	 = None
	notional      	 = None

	# There are two types of transactions- a transation can be sent with quantity, or notion (money amount).

	def __init__(self, order_pipe, transaction_type, ticker, side, order_type, value, time_in_force):
		self.order_pipe = order_pipe
		self.transaction_type = transaction_type
		self.ticker = ticker
		self.side = side
		self.order_type = order_type
		self.time_in_force = time_in_force

		if transaction_type == 'notional':
			self.notional = value
		if transaction_type == 'quantity':
			self.qty = value

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

		# negative qty? liquidate asset.
		if self.qty < 0:
			"liquidating asset: {}".format(self.ticker)
			logger.logp("liquidating asset: {}".format(self.ticker))
			return api.close_position(self.ticker)

		# otherwise just submit a regular order

		if self.transaction_type == 'notional':
			order = api.submit_order(
				symbol 	      = self.ticker,
				side   	      = self.side,
				type   	      = self.order_type,
				notional      = self.value,
				time_in_force = self.time_in_force)

		elif self.transaction_type == 'quantity':
			order = api.submit_order(
				symbol 	      = self.ticker,
				side   	      = self.side,
				type   	      = self.order_type,
				qty    	      = self.value,
				time_in_force = self.time_in_force)

		else:
			logger.logp('FATAL ERROR! incorrect transaction type')

		logger.logp(self.get_info())
		return order

	def get_info(self):
		return "submitted order: {}, qty {}, side {}, type {}, tif {}".format(
			self.ticker,
			self.qty,
			self.side,
			self.order_type,
			self.time_in_force)

def market_buy(order_pipe, ticker, notional):
	t = transaction(
		order_pipe       = order_pipe,
		transaction_type = 'notional',
		ticker           = ticker,
		side             = 'buy',
		order_type       = 'market',
		value            = notional,
		time_in_force    = 'fok')
	order_pipe.send(t)
	return order_pipe.recv()

# def market_buy(order_pipe, ticker, qty):
# 	t = transaction(order_pipe, ticker, 'buy', 'market', qty, 'fok')
# 	order_pipe.send(t)
# 	return order_pipe.recv()

# def market_sell(order_pipe, ticker, qty):
# 	t = transaction(order_pipe, ticker, 'sell', 'market', qty, 'fok')
# 	order_pipe.send(t)
# 	return order_pipe.recv()

# liquidates a position at market price
def market_liquidate(order_pipe, ticker):
	t = transaction(
		order_pipe       = order_pipe,
		transaction_type = 'quantity',
		ticker           = ticker,
		side             = 'sell',
		order_type       = 'market',
		value            = -1,
		time_in_force    = 'fok')
	order_pipe.send(t)
	return order_pipe.recv()