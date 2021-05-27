import os
import multiprocessing
import logging
import time
from datetime import datetime

LOG_LEVEL = logging.INFO

# for debugging
class Trace:
	def start(self):
		self.start = time.time()
	def end(self):
		end = time.time()
		delta = end-self.start
		print("MS [{}] NS [{}]".format(round(delta * 1000), delta))

def uniquify_filename(path):
	date = datetime.now().strftime("%m-%d-%Y_%H:%M:%S")
	filename, extension = os.path.splitext(path)
	return filename + "_" + date + extension

def main_setup():
	FORMAT = '%(asctime)-15s | %(message)s'
	filename = uniquify_filename('history.log')
	if not os.path.exists(filename):
		open(filename, "x")
	logging.basicConfig(format=FORMAT, filename=filename, level=LOG_LEVEL)
	global queue
	queue = multiprocessing.Queue()
	process_setup(queue)
	return queue

def process_setup(logging_queue):
	# configure out queue to be global to this processes namespace:
	# this queue gets copied to each sub-processes memory space,
	# hence why process_setup needs to be called
	global queue
	queue = logging_queue

def listen():
	# listen to any logging requests, and populate our log file using a mutex
	while True:
		global queue
		log = queue.get()
		if log['priority'] == 'debug': logging.debug(log['data'])
		if log['priority'] == 'info': logging.info(log['data'])
		if log['priority'] == 'warning': logging.warning(log['data'])
		if log['priority'] == 'error': logging.error(log['data'])
		if log['priority'] == 'critical': logging.critical(log['data'])
		if log['priority'] == 'TERMINATE': raise Exception("raised by TERMINATE")

def log(data='', priority='info'):
	global queue
	queue.put({'priority': priority, 'data': data})

def logp(data='', priority='info'):
	global queue
	print(data)
	queue.put({'priority': priority, 'data': data})

# called by a child process. onces called, termination from main process is signaled
def destroy(term_ex):
	print(term_ex)
	queue.put({'priority': 'TERMINATE', 'data': 'termination called from child process'})
def destroy():
	queue.put({'priority': 'TERMINATE', 'data': 'termination called from child process'})