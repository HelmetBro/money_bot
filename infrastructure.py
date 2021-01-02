import os
import multiprocessing
import logging
import time
import math
import datetime
import pandas

# custom algorithms
import algo
import security

# errors, signals, logging, etc
import logger
from signal import *
from func_timeout import FunctionTimedOut

# Alpaca api stuff
import alpaca_trade_api as tradeapi
api = tradeapi.REST()

TIMEOUT = 9 # seconds for function timeout (Alpaca makes 3 retrys at 3 seconds timeout for each)
ALPACA_SLEEP_CYCLE = 60 # in seconds. one munite before an api call

### TEMP v
tickers = {'AAPL', 'MSFT', 'TSLA', 'SBUX'}
### TEMP ^

# list of sub-processes for each ticker
child_processes = []

def main():
    # check all tickers to ensure they're supported by Alpaca
    for ticker in tickers:
        try:
            asset = api.get_asset(ticker)
            if asset.tradable == False:
                print("{} is within Alpaca, but not tradeable!".format(ticker))
                return
        except:
            print("{} is not Alpaca-compliant!".format(ticker))
            return

    # ensuring our account setup is okay
    account = api.get_account()
    account_status = "account status: {}".format(account.status)
    print(account_status)

    # starting our main process
    start_loop()

def start_loop():
    logging_queue = logger.main_setup()
    logger.log("starting main loop")

    # populate processes list with an instance per ticker
    for ticker in tickers:
        process = multiprocessing.Process(target=work, args=(logging_queue, ticker))
        process.start()
        child_processes.append(process)

    logger.listen()

def work(logging_queue, ticker):
    logger.process_setup(logging_queue)
    logger.log("subprocess for {} started".format(ticker))
    # create a security object for each process given the ticker
    sec = security.Security(ticker)
    while True:
        try:
            # wait our desired amount of seconds (as per Alpaca)
            time.sleep(ALPACA_SLEEP_CYCLE)
            
            # only run if the market is open
            if api.get_clock().is_open == False:
                logger.log("market is closed".format(), 'debug')
                continue

            # calling algorithms and using the last closing price
            macd_result = algo.macd(ticker)['close']
            rsi_result = algo.rsi(ticker)['close']
            cash = algo.buy_or_sell_macd_rsi(macd_result, rsi_result, sec)

        except FunctionTimedOut:
            logger.log("PID: {} TICKER: {} timed out! TIMEOUT = {}".format(os.getpid(), ticker, TIMEOUT), 'error')
            break

        # # wait our desired amount of seconds (as per Alpaca)
        # time.sleep(ALPACA_SLEEP_CYCLE)

    logger.log("PID: {} TICKER: {} is exiting".format(os.getpid(), ticker))

def cleanup(*args):
    for process in child_processes:
        print("terminating process {}".format(process.pid))
        logger.queue.close()
        process.terminate()
    os._exit(0)

if __name__ == "__main__":
    try:
        for sig in (SIGABRT, SIGINT, SIGTERM):
            signal(sig, cleanup)
        main()
    except Exception as e:
        print(e.message)
        cleanup()