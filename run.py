import os
import argparse
import infrastructure
import traceback
import time
import logger
from signal import signal, SIGABRT, SIGINT, SIGTERM

# parsing arguments and setting global BACKTRADING var
# Must be accessed by from run import BACKTRADING as BACKTRADING
parser = argparse.ArgumentParser()
parser.add_argument("-b", "--backtrader",
					help="runs algorithm with backtrading data",
					action="store_true")
BACKTRADING = parser.parse_args().backtrader

def force_kill(*args):
	child_process_cleanup()
	logger.logp("FORCED: terminating main process " + str(os.getpid()))
	time.sleep(0.5) # waiting for logging thread to catch up
	os.kill(os.getpid(), SIGABRT)

def child_process_cleanup(*args):
	logger.logp()
	for child in infrastructure.child_processes:
		logger.logp("terminating child process " + str(child.pid))
		os.kill(child.pid, SIGABRT)
		child.join()

if __name__ == "__main__":
	for sig in (SIGINT, SIGTERM):
		signal(sig, force_kill)
	while True:
		try:
			infrastructure.main()
		except Exception as e:
			logger.logp(e)
			logger.logp("fatal error. attempting to recover")
			child_process_cleanup()