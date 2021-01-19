import os
import multiprocessing
import logging
import time
import math
import datetime
import pandas
import backtrader as bt

# custom algorithms
import algo
import security

# errors, signals, logging, etc
import logger
from signal import signal, SIGINT, SIG_IGN
from func_timeout import FunctionTimedOut

# imported here for main() to ensure account is okay
import alpaca_trade_api as tradeapi

# custom trade-api wrapper
import process_api

TIMEOUT = 9 # seconds for function timeout (Alpaca makes 3 retrys at 3 seconds timeout for each)
ALPACA_SLEEP_CYCLE = 60 # in seconds. one munite before an api call
BACKTRADER = False

# TICKERS! If using backtrader, can only test using a single ticker. :(
# reason:
# error while consuming ws messages: Error while connecting to wss://data.alpaca.markets/stream:your connection is rejected while another connection is open under the same account
# tickers = {'TSLA'}
tickers = {'CYH', 'NI', 'UEPS', 'RGP', 'WEN', 'OHI', 'VER', 'CHD', 'AKAM', 'DLR', 'WLTW'}

# used only for main process to join() upon termination
child_processes = []

def main():
    api = tradeapi.REST()

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
        child_processes.append(process)
    
    for process in child_processes:
        process.start()

    logger.listen()

def work(logging_queue, ticker):
    # setting up alpaca api wrapper
    process_api.setup_api()

    # setting up logging/signals
    signal(SIGINT, SIG_IGN)
    logger.process_setup(logging_queue)
    logger.logp("subprocess for {} started".format(ticker))
    
    # create a security object for each process given the ticker
    sec = security.Security(ticker)

    if BACKTRADER:
        # call our run our back
        import backtrader_infra
        backtrader_infra.run(ticker)
        time.sleep(2)
        logger.destroy()

    while True:
        try:
            # wait our desired amount of seconds (as per Alpaca)
            # time.sleep(ALPACA_SLEEP_CYCLE)
            time.sleep(0.1)

            # only run if the market is open
            # if process_api.api.get_clock().is_open == False:
            #     logger.log("market is closed".format(), 'debug')
            #     continue

            # calling algorithms and make a decision
            # decision = algo.buy_or_sell_macd_rsi(ticker)
            decision = algo.buy_and_sell_david_custom(ticker)
            if decision == 'buy':
                sec.buy()
            if decision == 'sell':
                sec.sell()
            
        # except api.requests.exception HTTPError:
        #     logger.log("HTTPS error. retrying on next activation", 'error')
        except FunctionTimedOut as e:
            logger.log("PID: {} TICKER: {} timed out! TIMEOUT = {}, retrying on next activation".format(os.getpid(), ticker, TIMEOUT), 'error')
        except Exception as e:
            logger.log("PID: {} TICKER: {} caught fatal error!".format(os.getpid(), ticker), 'critical')
            logger.log(e, 'critical')
            # logger.destroy(e)