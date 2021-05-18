import listener
import pandas
import numpy

class algorithm(listener.listener):

	# max size for stored data. when this limit is reached, data lists
	# and pd's are all halfed (down to 100)
	MAX_DATA_SIZE = 50

	# pipe to send transactions through to main interface. stored here so all algo's can use
	order_pipe = None

	# need to flush a good chunk later when this array gets pretty big
	live_trades_data_pd  = pandas.DataFrame(columns=['p', 's'])
	live_quotes_data_pd  = pandas.DataFrame(columns=['p', 's', 'P', 'S'])
	live_bars_data_pd    = pandas.DataFrame(columns=['o', 'h', 'l', 'c', 'v'])
	live_updates_data    = []

	def __init__(self, order_pipe, readers):
		super().__init__(readers)
		self.order_pipe = order_pipe

	def get_trades(self, period):
		return self.live_trades_data_pd.iloc[-period:]
	def get_quotes(self, period):
		return self.live_quotes_data_pd.iloc[-period:]
	def get_bars(self, period):
		return self.live_bars_data_pd.iloc[-period:]
	def get_updates(self, period):
		return self.live_updates_data[-period:]

	### The following must remain separate functions due to GIL ###

	## trades-related watcher thread ##

	def on_trades(self):
		self.live_trades_data_pd.loc[len(self.live_trades_data_pd)] = self.trades_queue.get()
		if len(self.live_trades_data_pd) >= self.MAX_DATA_SIZE:
			self.live_trades_data_pd = numpy.array_split(self.live_trades_data_pd, 2)[1]
			self.live_trades_data_pd.reset_index(drop=True, inplace=True)

	def on_trades_get(self, period):
		self.on_trades()
		return self.get_trades(period)

	## quotes-related watcher thread ##

	def on_quotes(self):
		self.live_quotes_data_pd.loc[len(self.live_quotes_data_pd)] = self.quotes_queue.get()
		if len(self.live_quotes_data_pd) >= self.MAX_DATA_SIZE:
			self.live_quotes_data_pd = numpy.array_split(self.live_quotes_data_pd, 2)[1]
			self.live_quotes_data_pd.reset_index(drop=True, inplace=True)

	def on_quotes_get(self, period):
		self.on_quotes()
		return self.get_quotes(period)

	## bars-related watcher thread ##

	def on_bars(self):
		self.live_bars_data_pd.loc[len(self.live_bars_data_pd)] = self.bars_queue.get()
		if len(self.live_bars_data_pd) >= self.MAX_DATA_SIZE:
			self.live_bars_data_pd = numpy.array_split(self.live_bars_data_pd, 2)[1]
			self.live_bars_data_pd.reset_index(drop=True, inplace=True)

	def on_bars_get(self, period):
		self.on_bars()
		return self.get_bars(period)

	## updates-related watcher thread ##

	def on_updates(self):
		self.live_updates_data.append(self.updates_queue.get())
		if len(self.live_updates_data) >= self.MAX_DATA_SIZE:
			self.live_updates_data = numpy.array_split(self.live_updates_data, 2)[1]
			self.live_updates_data.reset_index(drop=True, inplace=True)

	def on_updates_get(self, period):
		self.on_updates()
		return self.get_updates(period)