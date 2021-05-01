from waiting import wait

import listener
import pandas
import run

class algorithm(listener.listener):

	order_pipe = None

	# need to flush a good chunk later when this array gets pretty big
	live_trades_data_list        = []
	live_quotes_data_list        = []
	live_trade_updates_data_list = []
	live_minute_bars_data_list   = []

	# live_minute_data_pd = None
	# live_second_data_pd = None

	account = None # need to init this on start up

	def __init__(self, order_pipe, trade_reader, quote_reader, bar_reader, update_reader):
		super().__init__(trade_reader, quote_reader, bar_reader, update_reader)
		self.order_pipe = order_pipe

	def get_account(self):
		if run.BACKTRADING:
			pass
		return self.account

	def get_minute_bars(self, period):
		if run.BACKTRADING:
			pass
		return self.live_minute_data_pd[0:period]

	def get_second_data(self, period):
		if run.BACKTRADING:
			pass
		return self.live_second_data_pd[0:period]

	# def on_trades(self):
	# 	# storing and appending to a list is much faster than a df. concating a df is fast.
	# 	wait(lambda: super.trades_has_update == True)
	# 	super.trades_lock.acquire()
	# 	self.trades = super.trades_data
	# 	super.trades_has_update = False
	# 	super.trades_lock.release()

	def on_quotes(self):
		# storing and appending to a list is much faster than a df. concating a df is fast.
		wait(lambda: super.minute_has_update == True)
		super.minute_lock.acquire()
		self.live_minute_data_list.append(super.minute_data)
		self.live_minute_data_pd = pandas.concat(self.live_minute_data_list, ignore_index=True)
		super.minute_has_update = False
		super.minute_lock.release()

	def on_second(self):
		# storing and appending to a list is much faster than a df. concating a df is fast.
		wait(lambda: super.second_has_update == True)
		super.second_lock.acquire()
		self.live_second_data_list.append(super.second_data)
		self.live_second_data_pd = pandas.concat(self.live_second_data_list, ignore_index=True)
		super.second_has_update = False
		super.second_lock.release()

	# can add on_status and on_account in future if needed