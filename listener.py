import threading

class listener:
	account_lock = threading.Lock()
	status_lock = threading.Lock()
	minute_lock = threading.Lock()
	second_lock = threading.Lock()

	listeners = None
	account = None # this should only be edited by one sub-thread
	status = None # this should only be edited by one sub-thread
	minute_data = None # this should only be edited by one sub-thread
	second_data = None # this should only be edited by one sub-thread

	account_has_update = False
	status_has_update = False
	minute_has_update = False
	second_has_update = False

	def __init__(self, account_updates, status_updates, minute_updates, second_updates):
		
		# make requests to get account data when created first before doing the below. WIP
		
		account_listener = threading.Thread(target=self.account_listener(account_updates), daemon=True)
		status_listener = threading.Thread(target=self.status_listener(status_updates), daemon=True)
		minute_listener = threading.Thread(target=self.minute_listener(minute_updates), daemon=True)
		second_listener = threading.Thread(target=self.second_listener(second_updates), daemon=True)
		self.listeners = [account_listener, status_listener, minute_listener, second_listener]
		for l in self.listeners:
			l.start()

	def account_listener(self, listener):
		while True:
			self.account_lock.acquire()
			self.account = listener.recv()
			self.account_has_update = True
			print(self.account)
			self.account_lock.release()

	def status_listener(self, listener):
		while True:
			self.status_lock.acquire()
			self.status = listener.recv()
			self.status_has_update = True
			print(self.status)
			self.second_lock.release()

	def minute_listener(self, listener):
		while True:
			self.minute_lock.acquire()
			self.minute_data = listener.recv()
			self.minute_has_update = True
			print(self.minute_data)
			self.second_lock.release()

	def second_listener(self, listener):
		while True:
			self.second_lock.acquire()
			self.second_data = listener.recv()
			self.second_has_update = True
			print(self.second_data)
			self.second_lock.release()