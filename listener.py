import threading

class listener:
	trades_lock      = threading.Lock()
	quotes_lock      = threading.Lock()
	updates_lock     = threading.Lock()
	minute_bars_lock = threading.Lock()


	trades_data      = None # this should only be edited by one sub-thread
	quotes_data      = None # this should only be edited by one sub-thread
	updates_data     = None # this should only be edited by one sub-thread
	minute_bars_data = None # this should only be edited by one sub-thread

	trades_has_update      = False
	quotes_has_update      = False
	updates_has_update     = False
	minute_bars_has_update = False

	def __init__(self, trade_reader, quote_reader, bar_reader, update_reader):

		# make request(s) to get account data when created first before doing the below W.I.P.

		trades_listener      = threading.Thread(target=self.trades_listener(trade_reader), daemon=True).start()
		quotes_listener      = threading.Thread(target=self.quotes_listener(quote_reader), daemon=True).start()
		updates_listener     = threading.Thread(target=self.updates_listener(update_reader), daemon=True).start()
		minute_bars_listener = threading.Thread(target=self.minute_bars_listener(bar_reader), daemon=True).start()

	def trades_listener(self, listener):
		while True:
			self.trades_lock.acquire()
			self.trades_data = listener.recv()
			self.trades_has_update = True
			print(self.trades_data)
			self.trades_lock.release()

	def quotes_listener(self, listener):
		while True:
			self.quotes_lock.acquire()
			self.quotes_data = listener.recv()
			self.quotes_has_update = True
			print(self.quotes_data)
			self.quotes_lock.release()

	def updates_listener(self, listener):
		while True:
			self.updates_lock.acquire()
			self.updates_data = listener.recv()
			self.updates_has_update = True
			print(self.updates_data)
			self.updates_lock.release()

	def minute_bars_listener(self, listener):
		while True:
			self.minute_bars_lock.acquire()
			self.minute_bars_data = listener.recv()
			self.minute_bars_has_update = True
			print(self.minute_bars_data)
			self.minute_bars_lock.release()