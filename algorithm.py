from waiting import wait

import listener
import pandas
import run

class algorithm(listener.listener):

	# max size for stored data. when this limit is reached, data lists
	# and pd's are all halfed (down to 200)
	MAX_DATA_SIZE = 400

	# pipe to send transactions through to main interface. stored here so all algo's can use
	order_pipe = None

	# need to flush a good chunk later when this array gets pretty big
	live_trades_data_list  = []
	live_quotes_data_list  = []
	live_bars_data_list    = []
	live_updates_data_list = []

	live_trades_data_pd  = []
	live_quotes_data_pd  = []
	live_bars_data_pd    = []
	live_updates_data_pd = []

	account = None # need to init this on start up

	def __init__(self, order_pipe, trade_reader, quote_reader, bar_reader, update_reader):
		super().__init__(trade_reader, quote_reader, bar_reader, update_reader)
		self.order_pipe = order_pipe

	def get_account(self):
		if run.BACKTRADING:
			pass
		return self.account

	def get_trades(self, period):
		if run.BACKTRADING:
			pass
		return self.live_trades_pd[0:period]

	def get_quotes(self, period):
		if run.BACKTRADING:
			pass
		return self.live_quotes_pd[0:period]

	def get_bars(self, period):
		if run.BACKTRADING:
			pass
		return self.live_bars_pd[0:period]

	def get_updates(self, period):
		if run.BACKTRADING:
			pass
		return self.live_updates_pd[0:period]

	### The following must remain separate functions due to GIL

	def on_trades(self):
		# storing and appending to a list is much faster than a df. concating a df is fast.
		wait(lambda: self.trades_has_update == True)
		self.trades_lock.acquire()
		self.live_trades_data_list.append(self.trades_data)
		self.live_trades_data_pd = pandas.concat(self.live_trades_data_list, ignore_index=True)

		if len(self.live_trades_data_list) >= self.MAX_DATA_SIZE:
			if len(self.live_trades_data_list) != len(self.live_trades_data_pd):
				raise Exception("trades data list and pd are different!")
			self.live_trades_data_list = self.live_trades_data_list[:-int(self.MAX_DATA_SIZE/2) or None]
			self.live_trades_data_pd = self.live_trades_data_pd[:-int(self.MAX_DATA_SIZE/2) or None]

		self.trades_has_update = False
		self.trades_lock.release()

	def on_quotes(self):
		# storing and appending to a list is much faster than a df. concating a df is fast.
		wait(lambda: self.quotes_has_update == True)
		super.quotes_lock.acquire()
		self.live_quotes_data_list.append(self.quotes_data)
		self.live_quotes_data_pd = pandas.concat(self.live_quotes_data_list, ignore_index=True)

		if len(self.live_quotes_data_list) >= self.MAX_DATA_SIZE:
			if len(self.live_quotes_data_list) != len(self.live_quotes_data_pd):
				raise Exception("quotes data list and pd are different!")
			self.live_quotes_data_list = self.live_quotes_data_list[:-int(self.MAX_DATA_SIZE/2) or None]
			self.live_quotes_data_pd = self.live_quotes_data_pd[:-int(self.MAX_DATA_SIZE/2) or None]

		self.quotes_has_update = False
		self.quotes_lock.release()

	def on_bars(self):
		# storing and appending to a list is much faster than a df. concating a df is fast.
		wait(lambda: self.bars_has_update == True)
		self.bars_lock.acquire()
		self.live_bars_data_list.append(self.bars_data)
		self.live_bars_data_pd = pandas.concat(self.live_bars_data_list, ignore_index=True)

		if len(self.live_bars_data_list) >= self.MAX_DATA_SIZE:
			if len(self.live_bars_data_list) != len(self.live_bars_data_pd):
				raise Exception("bars data list and pd are different!")
			self.live_bars_data_list = self.live_bars_data_list[:-int(self.MAX_DATA_SIZE/2) or None]
			self.live_bars_data_pd = self.live_bars_data_pd[:-int(self.MAX_DATA_SIZE/2) or None]

		self.bars_has_update = False
		self.bars_lock.release()

	def on_updates(self):
		# storing and appending to a list is much faster than a df. concating a df is fast.
		wait(lambda: self.updates_has_update == True)
		self.updates_lock.acquire()
		self.live_updates_data_list.append(self.updates_data)
		self.live_updates_data_pd = pandas.concat(self.live_updates_data_list, ignore_index=True)

		if len(self.live_updates_data_list) >= self.MAX_DATA_SIZE:
			if len(self.live_updates_data_list) != len(self.live_updates_data_pd):
				raise Exception("updates data list and pd are different!")
			self.live_updates_data_list = self.live_updates_data_list[:-int(self.MAX_DATA_SIZE/2) or None]
			self.live_updates_data_pd = self.live_updates_data_pd[:-int(self.MAX_DATA_SIZE/2) or None]

		self.updates_has_update = False
		self.updates_lock.release()