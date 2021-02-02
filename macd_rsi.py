from waiting import wait

import algorithm
import logger
import transaction
import algo_math

class macd_rsi(algorithm):
	buying_power = 0
	ticker = None

	long_period_macd = 26 # past 26 mintues
	short_period_macd = 12 # past 12 mintues
	period_rsi = 14 # past 14 mintues
	signal_ema_period = 9 # past 9 mintues

	def __init__(self, ticker, order_pipe, account_updates, status_updates, minute_updates, second_updates):
		super().__init__(order_pipe, account_updates, status_updates, minute_updates, second_updates)
		self.ticker = ticker

	def run(self):
		while True:
			super.on_minute()
			long_data_macd = super.get_minute_data(self.long_period_macd)
			short_data_macd = super.get_minute_data(self.short_period_macd)
			rsi_data = super.get_minute_data(self.period_rsi)
			recent_reliable_price = super.get_second_data(15)
			self.buy_or_sell_macd_rsi(long_data_macd, short_data_macd, rsi_data, recent_reliable_price)

	def buy_or_sell_macd_rsi(self, long_data_macd, short_data_macd, rsi_data, recent_reliable_price):
		# run both strats
		macd_signal_result = algo_math.macd_with_signal(long_data_macd, short_data_macd, self.signal_ema_period)['close']
		rsi_result = algo_math.rsi(rsi_data)['close']

		# make a decision to buy/sell
		if macd_signal_result > 0 and rsi_result < 33.33:
			transaction.market_buy(super.order_pipe, self.ticker, int(self.buy_power / recent_reliable_price['close']))
		elif macd_signal_result < 0 and rsi_result > 66.66:
			transaction.market_sell(super.order_pipe, self.ticker, )
		
		# if undesireable, don't make a transaction
		logger.log("{} -> macd_signal: {}, rsi: {} no trade signal thrown".format(
			self.ticker, macd_signal_result, rsi_result), 'debug')