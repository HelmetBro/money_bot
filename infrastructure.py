from macd_rsi import macd_rsi
import os
import multiprocessing
import threading
import traceback
import transaction

# errors, signals, logging, etc
import logger
from signal import signal, SIGINT, SIG_IGN
from func_timeout import FunctionTimedOut

# imported here for main() to ensure account is okay
import alpaca_trade_api as tradeapi
from alpaca_trade_api import StreamConn
api = tradeapi.REST()
conn = StreamConn()

TIMEOUT = 9 # seconds for function timeout (Alpaca makes 3 retrys at 3 seconds timeout for each)
ALPACA_SLEEP_CYCLE = 60 # in seconds. one minute before an api call

# tickers = {'BBBY', 'GME', 'NOK', 'AMC', 'SNDL', 'NAKD', 'CTRM', 'TRCH', 'IDEX', 'CCIV'}
tickers = {'GOVX', 'TGC', 'IDEX', 'PLTR', 'CNSP', 'USX', 'GRNQ', 'VISL', 'TRXC'}
# tickers = {'TSLA'}

# used only for main process to join() upon termination. do NOT use a process pool
child_processes = []

# pipe later created by multiprocessing to access 
account_update_streams = []
status_update_streams  = []
minute_update_streams  = []
second_update_streams  = []

@conn.on(r'^trade_updates$')
async def on_account_updates(conn, channel, account):
    for stream in account_update_streams:
        stream.send(account)

@conn.on(r'^status$')
async def on_status(conn, channel, data):
    for stream in status_update_streams:
        stream.send(data)

@conn.on(r'^AM$')
async def on_minute_bars(conn, channel, bar):
    for stream in minute_update_streams:
        stream.send(bar)

@conn.on(r'^A$')
async def on_second_bars(conn, channel, bar):
    for stream in second_update_streams:
        stream.send(bar)

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
    logger.logp("starting main loop")

    parent_order_pipe, child_order_pipe = multiprocessing.Pipe()

    # populate processes list with an instance per ticker
    for ticker in tickers:
        global account_update_streams
        global status_update_streams
        global minute_update_streams
        global second_update_streams
        account_reader, account_writer = multiprocessing.Pipe()
        status_reader, status_writer   = multiprocessing.Pipe()
        minute_reader, minute_writer   = multiprocessing.Pipe()
        second_reader, second_writer   = multiprocessing.Pipe()
        account_update_streams.append(account_writer)
        status_update_streams.append(status_writer)
        minute_update_streams.append(minute_writer)
        second_update_streams.append(second_writer)
        process = multiprocessing.Process(target=work, args=(
            logging_queue,
            child_order_pipe,
            account_reader,
            status_reader,
            minute_reader,
            second_reader,
            ticker))
        child_processes.append(process)

    # thread to initiate logging
    logger_thread = threading.Thread(target=logger.listen, daemon=True)
    logger_thread.start()

    # thread to initiate api requests
    api_thread = threading.Thread(target=transaction.listen, args=(parent_order_pipe), daemon=True)
    api_thread.start()

    for process in child_processes:
        process.start()

    conn.run(['trade_updates', 'alpacadatav1/AM.SPY']) # later change this to watch all tickers

def work(logging_queue, 
         order_pipe,
         account_updates,
         status_updates,
         minute_updates,
         second_updates,
         ticker):

    # setting up logging/signals
    signal(SIGINT, SIG_IGN) # ignore all interupts on sub processes
    logger.process_setup(logging_queue)
    logger.logp("subprocess for {} started".format(ticker))

    algorithm = macd_rsi(ticker,
                         order_pipe,
                         account_updates,
                         status_updates,
                         minute_updates,
                         second_updates)

    try:
        algorithm.run()
    except FunctionTimedOut as e:
        logger.log("PID: {} TICKER: {} timed out! TIMEOUT = {}, retrying on next activation".format(os.getpid(), ticker, TIMEOUT), 'error')
    except Exception as e:
        logger.log("PID: {} TICKER: {} caught error!".format(os.getpid(), ticker), 'critical')
        logger.logp(e, 'critical')
        logger.log(e.__traceback__)
        traceback.print_exc()
    except:
        logger.logp("special error was thrown", 'critical')