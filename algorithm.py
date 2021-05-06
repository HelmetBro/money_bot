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
	live_trades_data_pd  = pandas.DataFrame()
	live_quotes_data_pd  = pandas.DataFrame()
	live_bars_data_pd    = pandas.DataFrame(columns=['o', 'h', 'l', 'c', 'v'])
	live_updates_data_pd = pandas.DataFrame()

	account = None # need to init this on start up

	def __init__(self, order_pipe, trade_reader, quote_reader, bar_reader, update_reader):
		super().__init__(trade_reader, quote_reader, bar_reader, update_reader)
		self.order_pipe = order_pipe

	def get_account(self):
		return self.account

	def get_trades(self, period):
		return self.live_trades_data_pd[0:period]

	def get_quotes(self, period):
		return self.live_quotes_data_pd[0:period]

	def get_bars(self, period):
		return self.live_bars_data_pd[0:period]

	def get_updates(self, period):
		return self.live_updates_data_pd[0:period]

	### The following must remain separate functions due to GIL

	def on_trades(self):
		# storing and appending to a list is much faster than a df. concating a df is fast.
		wait(lambda: self.trades_has_update == True)
		self.trades_lock.acquire()
		self.live_trades_data_pd.loc[len(self.live_trades_data_pd)] = self.trades_data

		if len(self.live_trades_data_pd) >= self.MAX_DATA_SIZE:
			self.live_trades_data_pd = self.live_trades_data_pd[:-int(self.MAX_DATA_SIZE/2) or None]

		self.trades_has_update = False
		self.trades_lock.release()

	def on_quotes(self):
		# storing and appending to a list is much faster than a df. concating a df is fast.
		wait(lambda: self.quotes_has_update == True)
		super.quotes_lock.acquire()
		self.live_quotes_data_pd.loc[len(self.live_quotes_data_pd)] = self.quotes_data

		if len(self.live_quotes_data_pd) >= self.MAX_DATA_SIZE:
			self.live_quotes_data_pd = self.live_quotes_data_pd[:-int(self.MAX_DATA_SIZE/2) or None]

		self.quotes_has_update = False
		self.quotes_lock.release()

	def on_bars(self):
		# storing and appending to a list is much faster than a df. concating a df is fast.
		wait(lambda: self.bars_has_update == True)
		self.bars_lock.acquire()
		self.live_bars_data_pd.loc[len(self.live_bars_data_pd)] = self.bars_data

		if len(self.live_bars_data_pd) >= self.MAX_DATA_SIZE:
			self.live_bars_data_pd = self.live_bars_data_pd[:-int(self.MAX_DATA_SIZE/2) or None]

		self.bars_has_update = False
		self.bars_lock.release()

	def on_updates(self):
		# storing and appending to a list is much faster than a df. concating a df is fast.
		wait(lambda: self.updates_has_update == True)
		self.updates_lock.acquire()
		self.live_updates_data_pd.loc[len(self.live_updates_data_pd)] = self.updates_data

		if len(self.live_updates_data_pd) >= self.MAX_DATA_SIZE:
			self.live_updates_data_pd = self.live_updates_data_pd[:-int(self.MAX_DATA_SIZE/2) or None]

		self.updates_has_update = False
		self.updates_lock.release()