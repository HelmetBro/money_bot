import threading
import queue
import traceback
import logger

class listener:
	trades_queue  = queue.LifoQueue()
	quotes_queue  = queue.LifoQueue()
	updates_queue = queue.LifoQueue()
	bars_queue    = queue.LifoQueue()

	def __init__(self, readers):
		# make request(s) to get account data when created first before doing the below W.I.P.
		threading.Thread(target=self.trades_listener,  args=(readers[0],), daemon=True).start()
		threading.Thread(target=self.quotes_listener,  args=(readers[1],), daemon=True).start()
		threading.Thread(target=self.bars_listener,    args=(readers[2],), daemon=True).start()
		threading.Thread(target=self.updates_listener, args=(readers[3],), daemon=True).start()

	def trades_listener(self, listener):
		try:
			while True:
				self.trades_queue.put(listener.recv())
		except Exception as e:
			traceback.print_exc()
			logger.logp(e)

	def quotes_listener(self, listener):
		try:
			while True:
				self.quotes_queue.put(listener.recv())
		except Exception as e:
			traceback.print_exc()
			logger.logp(e)

	def bars_listener(self, listener):
		try:
			while True:
				self.bars_queue.put(listener.recv())
		except Exception as e:
			traceback.print_exc()
			logger.logp(e)

	def updates_listener(self, listener):
		try:
			while True:
				self.updates_queue.put(listener.recv())
		except Exception as e:
			traceback.print_exc()
			logger.logp(e)