import threading

class listener:
	trades_lock  = threading.Lock()
	quotes_lock  = threading.Lock()
	updates_lock = threading.Lock()
	bars_lock    = threading.Lock()

	trades_data  = None # this should only be edited by one sub-thread
	quotes_data  = None # this should only be edited by one sub-thread
	updates_data = None # this should only be edited by one sub-thread
	bars_data    = None # this should only be edited by one sub-thread

	trades_has_update  = False
	quotes_has_update  = False
	updates_has_update = False
	bars_has_update    = False

	def __init__(self, readers):
		# make request(s) to get account data when created first before doing the below W.I.P.
		threading.Thread(target=self.trades_listener, args=(readers[0],), daemon=True).start()
		threading.Thread(target=self.quotes_listener, args=(readers[1],), daemon=True).start()
		threading.Thread(target=self.bars_listener, args=(readers[2],), daemon=True).start()
		threading.Thread(target=self.updates_listener, args=(readers[3],), daemon=True).start()

	def trades_listener(self, listener):
		while True:
			temp_data = listener.recv()
			self.trades_lock.acquire()
			self.trades_data = temp_data
			self.trades_has_update = True
			self.trades_lock.release()

	def quotes_listener(self, listener):
		while True:
			temp_data = listener.recv()
			self.quotes_lock.acquire()
			self.quotes_data = temp_data
			self.quotes_has_update = True
			self.quotes_lock.release()

	def bars_listener(self, listener):
		while True:
			temp_data = listener.recv()
			self.bars_lock.acquire()
			self.bars_data = temp_data
			self.bars_has_update = True
			self.bars_lock.release()

	def updates_listener(self, listener):
		while True:
			temp_data = listener.recv()
			self.updates_lock.acquire()
			self.updates_data = temp_data
			self.updates_has_update = True
			self.updates_lock.release()