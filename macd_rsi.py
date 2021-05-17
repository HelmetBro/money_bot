import algorithm
import logger
import transaction
import algo_math
import threading

class macd_rsi(algorithm.algorithm):
	ticker = None
	qty = 0

	long_period_macd  = 6 # past 26 mintues
	short_period_macd = 3 # past 12 mintues
	period_rsi        = 3 # past 14 mintues
	signal_ema_period = 2  # past 9 mintues

	rsi_upper_bound = 52#66.66
	rsi_lower_bound = 48#33.33

	def __init__(self, ticker, order_pipe, readers, investable_qty):
		super().__init__(order_pipe, readers)
		self.ticker = ticker
		self.qty = investable_qty
		threading.Thread(target=self.update_qty, args=(), daemon=True).start()

	def update_qty(self):
		while True:
			update = super().on_updates(1)

			if update.event == 'fill':

				if update.side == 'buy':
					self.qty += update.filled_qty
					if (self.qty == 0):
						raise Exception("{} qty is 0 after sell order!".format(self.ticker))

				if update.side == 'sell':
					self.qty -= update.filled_qty
					if (self.qty != 0):
						raise Exception("{} qty is not 0 after sell order!".format(self.ticker))

	def run(self):
		while True:
			# calling this only logs bars data
			bars = super().on_bars(self.long_period_macd)

			# only continue if we have sufficient data (longest data period)
			if len(bars) < self.long_period_macd:
				continue

			# getting our data
			long_data_macd = super().get_bars(self.long_period_macd)
			short_data_macd = super().get_bars(self.short_period_macd)
			rsi_data = super().get_bars(self.period_rsi)

			# run both strats
			macd_signal_result = algo_math.macd_with_signal(long_data_macd, short_data_macd, self.signal_ema_period)['c']
			rsi_result = algo_math.rsi(rsi_data['c'])

			self.buy_or_sell_macd_rsi(macd_signal_result, rsi_result)

	def buy_or_sell_macd_rsi(self, macd_signal_result, rsi_result):
		# buy as much as possible
		if self.qty == 0 and macd_signal_result > 0 and rsi_result < self.rsi_lower_bound:
			logger.logp("{} -> macd_signal: {}, rsi: {} buying!".format(
			self.ticker, macd_signal_result, rsi_result), 'debug')
			transaction.market_buy_qty(self.order_pipe, self.ticker, self.qty)

		# liquidate entire position
		elif self.qty > 0 and macd_signal_result < 0 and rsi_result > self.rsi_upper_bound:
			logger.logp("{} -> macd_signal: {}, rsi: {} liquidating!".format(
			self.ticker, macd_signal_result, rsi_result), 'debug')
			transaction.market_liquidate(self.order_pipe, self.ticker)

		# if undesireable, don't make a transaction
		else:
			logger.logp("{} -> macd_signal: {}, rsi: {} no trade signal thrown".format(
			self.ticker, macd_signal_result, rsi_result), 'debug')