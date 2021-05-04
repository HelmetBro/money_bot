from waiting import wait

import algorithm
import logger
import transaction
import algo_math

class macd_rsi(algorithm.algorithm):
	buying_power = 0
	ticker = None

	long_period_macd  = 26 # past 26 mintues
	short_period_macd = 12 # past 12 mintues
	period_rsi        = 14 # past 14 mintues
	signal_ema_period = 9  # past 9 mintues

	rsi_upper_bound = 66.66
	rsi_lower_bound = 33.33

	def __init__(self, ticker, order_pipe, trade_reader, quote_reader, bar_reader, update_reader):
		super().__init__(order_pipe, trade_reader, quote_reader, bar_reader, update_reader)
		self.ticker = ticker

	def run(self):
		logger.logp("running!")
		while True:
			# calling this only logs bars data
			super().on_bars()

			# only continue if we have sufficient data (longest data period)
			while len(super().get_bars(self.long_period_macd)) < self.long_period_macd:
				print("continue")
				continue

			print("running!")


			# getting our data
			long_data_macd = super.get_bars(self.long_period_macd)
			short_data_macd = super.get_bars(self.short_period_macd)
			rsi_data = super.get_bars(self.period_rsi)

			# run both strats
			macd_signal_result = algo_math.macd_with_signal(long_data_macd, short_data_macd, self.signal_ema_period)['c']
			rsi_result = algo_math.rsi(rsi_data)['c']

			self.buy_or_sell_macd_rsi(macd_signal_result, rsi_result)

	def buy_or_sell_macd_rsi(self, macd_signal_result, rsi_result):
		# buy as much as possible
		if macd_signal_result > 0 and rsi_result < self.rsi_lower_bound:
			transaction.market_buy(super.order_pipe, self.ticker, self.buy_power)

		# liquidate entire position
		elif macd_signal_result < 0 and rsi_result > self.rsi_upper_bound:
			transaction.market_liquidate(super.order_pipe, self.ticker)

		# if undesireable, don't make a transaction
		logger.log("{} -> macd_signal: {}, rsi: {} no trade signal thrown".format(
			self.ticker, macd_signal_result, rsi_result), 'debug')