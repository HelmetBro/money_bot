import logger
from run import BACKTRADING as BACKTRADING

TIMEOUT = 9

# to be run in a thread by the main process
def listen(pipe, api):
	# listen to pipe, and submit requests accordingly
	while True:
		transaction = pipe.recv()
		transaction.submit(api)

class transaction:
	# pipe where transaction is sent upstream
	order_pipe = None

	# basic values that may fill a transation
	time_in_force    = None
	ticker		     = None
	side 		     = None
	order_type       = None # market/limit/etc
	transaction_type = None # quantity or notional
	value	      	 = None

	# There are two types of transactions- a transation can be sent with quantity, or notion (money amount).

	def __init__(self, order_pipe, transaction_type, ticker, side, order_type, value, time_in_force):
		self.order_pipe = order_pipe
		self.transaction_type = transaction_type
		self.ticker = ticker
		self.side = side
		self.order_type = order_type
		self.value = value
		self.time_in_force = time_in_force

	# only to be called by main processes sub-thread, listen()
	def submit(self, api):

		# negative qty? liquidate asset.
		if self.transaction_type == 'quantity' and self.value < 0:
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
		return "submitted order: ticker [{}] transaction type [{}] side [{}] order type [{}] value [{}] tif [{}]".format(
					self.ticker,
					self.transaction_type,
					self.side,
					self.order_type,
					self.value,
					self.time_in_force)

def market_buy_notional(order_pipe, ticker, notional):
	t = transaction(
		order_pipe       = order_pipe,
		transaction_type = 'notional',
		ticker           = ticker,
		side             = 'buy',
		order_type       = 'market',
		value            = notional,
		time_in_force    = 'fok')
	if BACKTRADING:
		logger.logp(t.get_info())
		return
	order_pipe.send(t)

def market_buy_qty(order_pipe, ticker, qty):
	t = transaction(
		order_pipe       = order_pipe,
		transaction_type = 'quantity',
		ticker           = ticker,
		side             = 'buy',
		order_type       = 'market',
		value            = qty,
		time_in_force    = 'fok')
	if BACKTRADING:
		logger.logp(t.get_info())
		return
	order_pipe.send(t)

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
	if BACKTRADING:
		logger.logp(t.get_info())
		return
	order_pipe.send(t)