import os
import multiprocessing
import time
import traceback
import backtrader_setup

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

# TICKERS! If using backtrader, can only test using a single ticker. :(
# reason:
# error while consuming ws messages: Error while connecting to wss://data.alpaca.markets/stream:your connection is rejected while another connection is open under the same account
# tickers = {'GOVX', 'TGC', 'IDEX', 'PLTR', 'CNSP', 'USX', 'GRNQ', 'VISL', 'TRXC'}
tickers = {'TSLA'}

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

    if backtrader_setup.BACKTRADER:
        # call our bracktrader and exit
        try:
            backtrader_setup.run(sec)
            time.sleep(2)
            logger.destroy()
            return
        except Exception as e:
            print(e)
            traceback.print_exc()
            return

    while True:
        try:
            # wait our desired amount of seconds (as per Alpaca)
            time.sleep(ALPACA_SLEEP_CYCLE)

            # only run if the market is open
            if process_api.api.get_clock().is_open == False:
                logger.log("market is closed".format(), 'debug')
                continue

            # calling algorithms and make a decision
            algo.buy_and_sell_david_custom(sec)
            # algo.buy_or_sell_macd_rsi(sec)
            
        # except api.requests.exception HTTPError:
        #     logger.log("HTTPS error. retrying on next activation", 'error')
        except FunctionTimedOut as e:
            logger.log("PID: {} TICKER: {} timed out! TIMEOUT = {}, retrying on next activation".format(os.getpid(), ticker, TIMEOUT), 'error')
        except Exception as e:
            logger.log("PID: {} TICKER: {} caught error!".format(os.getpid(), ticker), 'critical')
            logger.logp(e, 'critical')
            logger.log(e.__traceback__)
            traceback.print_exc()
            # logger.destroy(e)