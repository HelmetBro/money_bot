import threading

class listener:
	trades_data_lock  = threading.Lock()
	quotes_data_lock  = threading.Lock()
	updates_data_lock = threading.Lock()
	bars_data_lock    = threading.Lock()

	trades_update_lock  = threading.Lock()
	quotes_update_lock  = threading.Lock()
	updates_update_lock = threading.Lock()
	bars_update_lock    = threading.Lock()

	# these must be acquired to prevent updates with no new data on start
	trades_update_lock.acquire()
	quotes_update_lock.acquire()
	updates_update_lock.acquire()
	bars_update_lock.acquire()

	trades_data  = None # this should only be edited by one sub-thread
	quotes_data  = None # this should only be edited by one sub-thread
	updates_data = None # this should only be edited by one sub-thread
	bars_data    = None # this should only be edited by one sub-thread

	def __init__(self, readers):
		# make request(s) to get account data when created first before doing the below W.I.P.
		threading.Thread(target=self.trades_listener, args=(readers[0],), daemon=True).start()
		threading.Thread(target=self.quotes_listener, args=(readers[1],), daemon=True).start()
		threading.Thread(target=self.bars_listener, args=(readers[2],), daemon=True).start()
		threading.Thread(target=self.updates_listener, args=(readers[3],), daemon=True).start()

	def trades_listener(self, listener):
		while True:
			temp_data = listener.recv()
			self.trades_data_lock.acquire()
			self.trades_data = temp_data
			try:
				self.trades_update_lock.release()
			except:
				pass
			self.trades_data_lock.release()

	def quotes_listener(self, listener):
		while True:
			temp_data = listener.recv()
			self.quotes_data_lock.acquire()
			self.quotes_data = temp_data
			try:
				self.quotes_update_lock.release()
			except:
				pass
			self.quotes_data_lock.release()

	def bars_listener(self, listener):
		while True:
			temp_data = listener.recv()
			self.bars_data_lock.acquire()
			self.bars_data = temp_data
			try:
				self.bars_update_lock.release()
			except:
				pass
			self.bars_data_lock.release()

	def updates_listener(self, listener):
		while True:
			temp_data = listener.recv()
			self.updates_data_lock.acquire()
			self.updates_data = temp_data
			try:
				self.updates_update_lock.release()
			except:
				pass
			self.updates_data_lock.release()