from macd_rsi import macd_rsi
from run import BACKTRADING
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
from alpaca_trade_api.stream import Stream

TIMEOUT = 9 # seconds for function timeout (Alpaca makes 3 retrys at 3 seconds timeout for each)
ALPACA_SLEEP_CYCLE = 60 # in seconds. one minute before an api call
FEED = 'iex' # 'sip' for paid subscription

api = tradeapi.REST()
stream = Stream(data_feed=FEED, raw_data=True)

# tickers = ['BBBY', 'GME', 'NOK', 'AMC', 'SNDL', 'NAKD', 'CTRM', 'TRCH', 'IDEX', 'CCIV']
# tickers = ['GOVX', 'TGC', 'IDEX', 'PLTR', 'CNSP', 'USX', 'GRNQ', 'VISL', 'TRXC']
tickers = ['TSLA', 'AAPL', 'MSFT']

# used only for main process to join() upon termination. do NOT use a process pool
child_processes = []

# pipe later created by multiprocessing to access
trade_stream   = []
quote_stream   = []
bars_stream    = []
updates_stream = []

async def trade_callback(t):
    return
    print('trade', t)

async def quote_callback(q):
    return
    print('quote', q)

async def bars_callback(b):
    print('bars', b)

async def trade_updates_callback(tu):
    print('updates', tu)


# @conn.on(r'^trade_updates$')
# async def on_account_updates(conn, channel, account):
#     logger.logp("trade")
#     for stream in account_update_streams:
#         if stream['ticker'] == channel:
#             stream['writer'].send(account)

# @conn.on(r'^status$')
# async def on_status(conn, channel, data):
#     logger.logp("status")
#     for stream in status_update_streams:
#         stream.send(data)

# @conn.on(r'^AM$')
# async def on_minute_bars(conn, channel, bar):
#     logger.logp("minute")
#     for stream in minute_update_streams:
#         stream.send(bar)

# @conn.on(r'^A$')
# async def on_second_bars(conn, channel, bar):
#     logger.logp("second")
#     for stream in second_update_streams:
#         stream.send(bar)

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
        # setting up our streams

        global trade_stream
        global quote_stream   # WIP ON THIS. THIS IS INCORRECT!!
        global bars_stream
        global updates_stream
        trade_reader, trade_writer     = multiprocessing.Pipe()
        quote_reader, quote_writer     = multiprocessing.Pipe()
        bar_reader, bar_writer       = multiprocessing.Pipe()
        update_reader, update_writer = multiprocessing.Pipe()
        trade_stream.append(  {'ticker': ticker, 'writer': trade_writer})
        quote_stream.append(  {'ticker': ticker, 'writer': quote_writer})
        bars_stream.append(   {'ticker': ticker, 'writer': bar_writer})
        updates_stream.append({'ticker': ticker, 'writer': update_writer})

        # creating processes for each ticker
        process = multiprocessing.Process(target=work, args=(
            logging_queue,
            child_order_pipe,
            trade_reader,
            quote_reader,
            bar_reader,
            update_reader,
            ticker))
        child_processes.append(process)

        #subscribing to each ticker
        stream.subscribe_trades(trade_callback, ticker)
        stream.subscribe_quotes(quote_callback, ticker)
        stream.subscribe_bars(bars_callback, ticker)
        stream.subscribe_trade_updates(trade_updates_callback)

    # thread to initiate logging to run in a background thread on main process
    logger_thread = threading.Thread(target=logger.listen, daemon=True)
    logger_thread.start()

    # thread to handle api requests from Alpaca, and feed children
    api_thread = threading.Thread(target=transaction.listen, args=(parent_order_pipe,), daemon=True)
    api_thread.start()

    # for process in child_processes:
    #     process.start()

    if not BACKTRADING:
        stream.run()

def work(logging_queue,
         order_pipe,
         trade_reader,
         quote_reader,
         bar_reader,
         update_reader,
         ticker):

    # setting up logging/signals
    signal(SIGINT, SIG_IGN) # ignore all interupts on sub processes
    logger.process_setup(logging_queue)
    logger.logp("subprocess for {} started".format(ticker))

    # choose our algorithm can put any here
    algorithm = macd_rsi(ticker,
                         order_pipe,
                         trade_reader,
                         quote_reader,
                         bar_reader,
                         update_reader)

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