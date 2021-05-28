import threading
import queue
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
		while True:
			try:
				data = listener.recv()
				self.trades_queue.put(data)
			except Exception as e:
				logger.logp(e)

	def quotes_listener(self, listener):
		while True:
			try:
				data = listener.recv()
				self.quotes_queue.put(data)
			except Exception as e:
				logger.logp(e)

	def bars_listener(self, listener):
		while True:
			try:
				data = listener.recv()
				self.bars_queue.put(data)
			except Exception as e:
				logger.logp(e)

	def updates_listener(self, listener):
		while True:
			try:
				data = listener.recv()
				self.updates_queue.put(data)
			except Exception as e:
				logger.logp(e)