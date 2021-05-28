import algorithm
import logger
import transaction
import algo_math
import threading

class macd_rsi(algorithm.algorithm):
	ticker = None
	investable_qty = 0 # identical to buying power, until they fix 'notional'

	long_period_macd  = 26 # past 26 mintues
	short_period_macd = 12 # past 12 mintues
	signal_ema_period = 9  # past 9 mintues

	period_rsi      = 14 # past 14 mintues
	rsi_upper_bound = 55 # 66.66 - this is aggressive. 70 is standard
	rsi_lower_bound = 45 # 33.33 - this is aggressive. 30 is standard

	def __init__(self, ticker, order_pipe, readers, investable_qty):
		super().__init__(order_pipe, readers)
		self.ticker = ticker
		self.investable_qty = investable_qty
		threading.Thread(target=self.update_qty, args=(), daemon=True).start()

	def update_qty(self):
		while True:
			try:
				# get latest update
				update = super().on_updates_get(1)

				if update.event == 'fill':

					if update.side == 'buy':
						self.investable_qty -= update.filled_qty
						if (self.investable_qty != 0):
							raise Exception("{} investable_qty isn't 0 after buy order!".format(self.ticker))

					if update.side == 'sell':
						self.investable_qty += update.filled_qty
						if (self.investable_qty == 0):
							raise Exception("{} investable_qty is 0 after sell order!".format(self.ticker))

			except Exception as e:
				logger.logp(e)

	def run(self):
		while True:
			# calling this only logs bars data
			bars = super().on_bars_get(self.long_period_macd)

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
		if self.investable_qty >= 0 and macd_signal_result > 0 and rsi_result < self.rsi_lower_bound:
			logger.logp("{} -> macd_signal: {}, rsi: {} buying!".format(
					    self.ticker, macd_signal_result, rsi_result))
			transaction.market_buy_qty(self.order_pipe, self.ticker, self.investable_qty)

		# liquidate entire position
		elif self.investable_qty == 0 and macd_signal_result < 0 and rsi_result > self.rsi_upper_bound:
			logger.logp("qty", self.investable_qty)
			logger.logp("{} -> macd_signal: {}, rsi: {} liquidating!".format(
						self.ticker, macd_signal_result, rsi_result))
			transaction.market_liquidate(self.order_pipe, self.ticker)

		# if undesireable, don't make a transaction
		else:
			logger.logp("{} -> macd_signal: {}, rsi: {} no trade signal thrown".format(
						self.ticker, macd_signal_result, rsi_result))