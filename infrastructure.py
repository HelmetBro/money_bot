from macd_rsi import macd_rsi
import os
from run import BACKTRADING as BACKTRADING
import multiprocessing
import threading
import traceback
import transaction
import time
import asyncio
import copy
import account_setup

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
# tickers = ['TSLA', 'AAPL', 'MSFT']
tickers = ['TSLA']

# used only for main process to join() upon termination. do NOT use a process pool
child_processes = []

# pipe later created by multiprocessing to access
trade_stream   = []
quote_stream   = []
bars_stream    = []
updates_stream = []

### testing
t1 = {'T': 't', 'i': 9264, 'S': 'MSFT', 'x': 'V', 'p': 251.33, 's': 1, 'c': ['@', 'I'], 'z': 'C'}
t2 = {'T': 't', 'i': 9265, 'S': 'MSFT', 'x': 'V', 'p': 251.315, 's': 1, 'c': ['@', 'I'], 'z': 'C'}
t3 = {'T': 't', 'i': 9266, 'S': 'MSFT', 'x': 'V', 'p': 251.3, 's': 17, 'c': ['@', 'I'], 'z': 'C'}
t4 = {'T': 't', 'i': 9267, 'S': 'MSFT', 'x': 'V', 'p': 251.3, 's': 19, 'c': ['@', 'I'], 'z': 'C'}
t5 = {'T': 't', 'i': 17287, 'S': 'AAPL', 'x': 'V', 'p': 133.45, 's': 100, 'c': ['@'], 'z': 'C'}
t6 = {'T': 't', 'i': 17288, 'S': 'AAPL', 'x': 'V', 'p': 133.45, 's': 50, 'c': ['@', 'I'], 'z': 'C'}
t7 = {'T': 't', 'i': 9268, 'S': 'MSFT', 'x': 'V', 'p': 251.315, 's': 2, 'c': ['@', 'I'], 'z': 'C'}
t8 = {'T': 't', 'i': 12032, 'S': 'TSLA', 'x': 'V', 'p': 673.14, 's': 1, 'c': ['@', 'I'], 'z': 'C'}
t9 = {'T': 't', 'i': 9269, 'S': 'MSFT', 'x': 'V', 'p': 251.31, 's': 1, 'c': ['@', 'I'], 'z': 'C'}

q1 = {'T': 'q', 'S': 'AAPL', 'bx': 'V', 'bp': 133.56, 'bs': 4, 'ax': 'V', 'ap': 133.58, 'as': 1, 'c': ['R'], 'z': 'C'}
q2 = {'T': 'q', 'S': 'AAPL', 'bx': 'V', 'bp': 133.57, 'bs': 4, 'ax': 'V', 'ap': 134.2, 'as': 1, 'c': ['R'], 'z': 'C'}
q3 = {'T': 'q', 'S': 'MSFT', 'bx': 'V', 'bp': 250.0, 'bs': 1, 'ax': 'V', 'ap': 251.44, 'as': 2, 'c': ['R'], 'z': 'C'}
q4 = {'T': 'q', 'S': 'TSLA', 'bx': 'V', 'bp': 673.25, 'bs': 1, 'ax': 'V', 'ap': 696.28, 'as': 1, 'c': ['R'], 'z': 'C'}
q5 = {'T': 'q', 'S': 'MSFT', 'bx': 'V', 'bp': 250.0, 'bs': 1, 'ax': 'V', 'ap': 251.4, 'as': 1, 'c': ['R'], 'z': 'C'}
q6 = {'T': 'q', 'S': 'MSFT', 'bx': 'V', 'bp': 250.0, 'bs': 1, 'ax': 'V', 'ap': 251.41, 'as': 2, 'c': ['R'], 'z': 'C'}
q7 = {'T': 'q', 'S': 'AAPL', 'bx': 'V', 'bp': 133.57, 'bs': 3, 'ax': 'V', 'ap': 134.2, 'as': 1, 'c': ['R'], 'z': 'C'}
q8 = {'T': 'q', 'S': 'AAPL', 'bx': 'V', 'bp': 133.56, 'bs': 3, 'ax': 'V', 'ap': 134.2, 'as': 1, 'c': ['R'], 'z': 'C'}
q9 = {'T': 'q', 'S': 'TSLA', 'bx': 'V', 'bp': 668.0, 'bs': 1, 'ax': 'V', 'ap': 696.28, 'as': 1, 'c': ['R'], 'z': 'C'}

b1 = {'T': 'b', 'S': 'TSLA', 'o': 672.94, 'h': 672.94, 'l': 672.61, 'c': 672.81, 'v': 729}
b2 = {'T': 'b', 'S': 'AAPL', 'o': 133.49, 'h': 133.5, 'l': 133.325, 'c': 133.33, 'v': 3436}
b3 = {'T': 'b', 'S': 'TSLA', 'o': 672.85, 'h': 673.83, 'l': 672.85, 'c': 673.69, 'v': 6728}
b4 = {'T': 'b', 'S': 'MSFT', 'o': 251.2, 'h': 251.25, 'l': 251.185, 'c': 251.245, 'v': 2752}
b5 = {'T': 'b', 'S': 'AAPL', 'o': 133.31, 'h': 133.4, 'l': 133.31, 'c': 133.38, 'v': 2441}
b6 = {'T': 'b', 'S': 'TSLA', 'o': 673.78, 'h': 674.245, 'l': 673.78, 'c': 674.245, 'v': 1795}
b7 = {'T': 'b', 'S': 'MSFT', 'o': 251.265, 'h': 251.335, 'l': 251.25, 'c': 251.25, 'v': 2236}
b8 = {'T': 'b', 'S': 'AAPL', 'o': 133.37, 'h': 133.39, 'l': 133.37, 'c': 133.38, 'v': 895}

tsla_bars = [

    {'T': 'b', 'S': 'TSLA', 'o': 5, 'h': 672.94, 'l': 672.61, 'c': 5.23, 'v': 729},
    {'T': 'b', 'S': 'TSLA', 'o': 5, 'h': 672.94, 'l': 672.61, 'c': 7.51, 'v': 729},
    {'T': 'b', 'S': 'TSLA', 'o': 5, 'h': 672.94, 'l': 672.61, 'c': 5.85, 'v': 729},
    {'T': 'b', 'S': 'TSLA', 'o': 5, 'h': 672.94, 'l': 672.61, 'c': 3.91, 'v': 729},
    {'T': 'b', 'S': 'TSLA', 'o': 5, 'h': 672.94, 'l': 672.61, 'c': 5.96, 'v': 729},
    {'T': 'b', 'S': 'TSLA', 'o': 5, 'h': 672.94, 'l': 672.61, 'c': 9.75, 'v': 729},
    {'T': 'b', 'S': 'TSLA', 'o': 5, 'h': 672.94, 'l': 672.61, 'c': 5.95, 'v': 729},
    {'T': 'b', 'S': 'TSLA', 'o': 5, 'h': 672.94, 'l': 672.61, 'c': 1.19, 'v': 729},
    {'T': 'b', 'S': 'TSLA', 'o': 5, 'h': 672.94, 'l': 672.61, 'c': 4.10, 'v': 729},
    {'T': 'b', 'S': 'TSLA', 'o': 5, 'h': 672.94, 'l': 672.61, 'c': 5.32, 'v': 729},
    {'T': 'b', 'S': 'TSLA', 'o': 5, 'h': 672.94, 'l': 672.61, 'c': 6.63, 'v': 729},
    {'T': 'b', 'S': 'TSLA', 'o': 5, 'h': 672.94, 'l': 672.61, 'c': 5.85, 'v': 729},
    {'T': 'b', 'S': 'TSLA', 'o': 5, 'h': 672.94, 'l': 672.61, 'c': 4.94, 'v': 729},
    {'T': 'b', 'S': 'TSLA', 'o': 5, 'h': 672.94, 'l': 672.61, 'c': 2.94, 'v': 729},
    {'T': 'b', 'S': 'TSLA', 'o': 5, 'h': 672.94, 'l': 672.61, 'c': 4.01, 'v': 729},
    {'T': 'b', 'S': 'TSLA', 'o': 5, 'h': 672.94, 'l': 672.61, 'c': 6.94, 'v': 729},
    {'T': 'b', 'S': 'TSLA', 'o': 4, 'h': 672.94, 'l': 672.61, 'c': 9.18, 'v': 729},
    {'T': 'b', 'S': 'TSLA', 'o': 4, 'h': 672.94, 'l': 672.61, 'c': 6.56, 'v': 729},
    {'T': 'b', 'S': 'TSLA', 'o': 4, 'h': 672.94, 'l': 672.61, 'c': 1.23, 'v': 729},
    {'T': 'b', 'S': 'TSLA', 'o': 4, 'h': 672.94, 'l': 672.61, 'c': 4.42, 'v': 729},
    {'T': 'b', 'S': 'TSLA', 'o': 3, 'h': 672.94, 'l': 672.61, 'c': 3.45, 'v': 729},
    {'T': 'b', 'S': 'TSLA', 'o': 3, 'h': 672.94, 'l': 672.61, 'c': 10.95, 'v': 729},
    {'T': 'b', 'S': 'TSLA', 'o': 3, 'h': 672.94, 'l': 672.61, 'c': 30.11, 'v': 729},
    {'T': 'b', 'S': 'TSLA', 'o': 30, 'h': 672.94, 'l': 672.61, 'c': 70.54, 'v': 729},
    {'T': 'b', 'S': 'TSLA', 'o': 70, 'h': 672.94, 'l': 672.61, 'c': 60.23, 'v': 729},
    {'T': 'b', 'S': 'TSLA', 'o': 70, 'h': 672.94, 'l': 672.61, 'c': 70.77, 'v': 729},
    {'T': 'b', 'S': 'TSLA', 'o': 70, 'h': 672.94, 'l': 672.61, 'c': 80.01, 'v': 729},
    {'T': 'b', 'S': 'TSLA', 'o': 80, 'h': 672.94, 'l': 672.61, 'c': 90.74, 'v': 729},
    {'T': 'b', 'S': 'TSLA', 'o': 90, 'h': 672.94, 'l': 672.61, 'c': 100.47, 'v': 729},
    {'T': 'b', 'S': 'TSLA', 'o': 100, 'h': 672.94, 'l': 672.61, 'c': 500.11, 'v': 729},
]

async def trade_callback(t):
    del t['T']
    ticker = t.pop('S', None)
    for stream in trade_stream:
        if stream['ticker'] == ticker:
            stream['writer'].send(t)

async def quote_callback(q):
    del q['T']
    ticker = q.pop('S', None)
    for stream in quote_stream:
        if stream['ticker'] == ticker:
            stream['writer'].send(q)

async def bars_callback(b):
    del b['T']
    ticker = b.pop('S', None)
    for stream in bars_stream:
        if stream['ticker'] == ticker:
            stream['writer'].send(b)

async def updates_callback(u):
    del u['T']
    ticker = u.pop('S', None)
    for stream in updates_stream:
        if stream['ticker'] == ticker:
            stream['writer'].send(u)

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
    print ("account status: ", account.status)

    # add current tickers to our tickers list, and get current invested positions
    positions = account_setup.add_current_tickers(api, tickers)

    # starting our main process
    start_loop(positions, float(account.cash))

def start_loop(positions, cash):
    logging_queue = logger.main_setup()
    logger.logp("starting main loop")

    parent_order_pipe, child_order_pipe = multiprocessing.Pipe()

    # populate processes list with an instance per ticker
    for ticker in tickers:

        # setting up our streams
        global trade_stream
        global quote_stream
        global bars_stream
        global updates_stream
        trade_reader, trade_writer     = multiprocessing.Pipe()
        quote_reader, quote_writer     = multiprocessing.Pipe()
        bar_reader, bar_writer         = multiprocessing.Pipe()
        update_reader, update_writer   = multiprocessing.Pipe()
        trade_stream.append(  {'ticker': ticker, 'writer': trade_writer})
        quote_stream.append(  {'ticker': ticker, 'writer': quote_writer})
        bars_stream.append(   {'ticker': ticker, 'writer': bar_writer})
        updates_stream.append({'ticker': ticker, 'writer': update_writer})

        readers = [trade_reader, quote_reader, bar_reader, update_reader];

        # calculate how much cash each ticker gets to invest (0 if there's already an active position)
        # from that, get the number of shares able to be bought. -0.05 to ensure order goes through
        investable_cash = account_setup.calc_investable_cash(cash, ticker, tickers, positions)
        investable_qty = int(investable_cash / (api.get_last_trade(ticker).price - 0.05))

        # creating processes for each ticker
        process = multiprocessing.Process(target=work, args=(
            logging_queue,
            child_order_pipe,
            readers,
            ticker,
            investable_qty))
        child_processes.append(process)

        #subscribing to each ticker
        stream.subscribe_trades(trade_callback, ticker)
        stream.subscribe_quotes(quote_callback, ticker)
        stream.subscribe_bars(bars_callback, ticker)
        stream.subscribe_trade_updates(updates_callback)

    # thread to initiate logging to run in a background thread on main process
    logger_thread = threading.Thread(target=logger.listen, daemon=True)
    logger_thread.start()

    # thread to handle api requests from Alpaca, and feed children
    api_thread = threading.Thread(target=transaction.listen, args=(parent_order_pipe, api,), daemon=True)
    api_thread.start()

    for process in child_processes:
        process.start()

    # while BACKTRADING:
    if BACKTRADING:
        old_loop = asyncio.get_event_loop()
        new_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(new_loop)
        while True:
            for x in range(30):
                time.sleep(0.5)
                asyncio.run(bars_callback(copy.deepcopy(tsla_bars[x])))
        asyncio.set_event_loop(old_loop)

    stream.run() # this is blocking

def work(logging_queue,
         order_pipe,
         readers,
         ticker,
         investable_qty):

    # setting up logging/signals
    signal(SIGINT, SIG_IGN) # ignore all interupts on sub processes
    logger.process_setup(logging_queue)
    logger.logp("subprocess for {} started".format(ticker))

    # choose our algorithm can put any here
    algorithm = macd_rsi(ticker,
                         order_pipe,
                         readers,
                         investable_qty)
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