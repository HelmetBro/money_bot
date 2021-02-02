from waiting import wait

import listener
import pandas
import run

class algorithm(listener):

	order_pipe = None

	live_minute_data_list = []
	live_second_data_list = []
	live_minute_data_pd = None
	live_second_data_pd = None

	def __init__(self, order_pipe, account_updates, status_updates, minute_updates, second_updates):
		super().__init__(account_updates, status_updates, minute_updates, second_updates)
		self.order_pipe = order_pipe

	def get_minute_data(self, period):
		if run.BACKTRADING:
			pass
		return self.live_minute_data_pd[0:period]

	def get_second_data(self, period):
		if run.BACKTRADING:
			pass
		return self.live_second_data_pd[0:period]

	def on_minute(self):
		# storing and appending to a list is much faster than a df. concating a df is fast.
		wait(lambda: super.minute_has_update == True)
		super.minute_lock.acquire()
		self.live_minute_data_list.append(super.minute_data)
		super.minute_lock.release()
		self.live_minute_data_pd = pandas.concat(self.live_minute_data_list, ignore_index=True)
		super.minute_has_update = False

	def on_second(self):
		# storing and appending to a list is much faster than a df. concating a df is fast.
		wait(lambda: super.second_has_update == True)
		super.second_lock.acquire()
		self.live_second_data_list.append(super.second_data)
		super.second_lock.release()
		self.live_second_data_pd = pandas.concat(self.live_second_data_list, ignore_index=True)
		super.second_has_update = False

	# can add on_status and on_account in future if needed