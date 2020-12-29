import os
import multiprocessing
import logging
import time
import math
import datetime
import pandas

# timeouts, errors, signals, etc
from func_timeout import func_set_timeout, FunctionTimedOut
from signal import *

# Alpaca stuff
import alpaca_trade_api as tradeapi
api = tradeapi.REST()
account = api.get_account()

# logging
FORMAT = '%(asctime)-15s | %(message)s'
filename = 'history.log'
if os.path.exists(filename): os.remove(filename)
logging.basicConfig(format=FORMAT, filename=filename, level=logging.DEBUG)

TIMEOUT = 5 # seconds for function call timeout
ALPACA_SLEEP_CYCLE = 60 # in seconds. one munite before an api call

### TEMP v
tickers = {'AAPL', 'MSFT', 'TSLA'}
### TEMP ^

# list of sub-processes for each ticker
child_processes = []

def main():
    # ensuring our account setup is okay
    account_status = "account status: {}".format(account.status)
    print(account_status)
    logging.info(account_status)

    # check if tickers are tradable on Alpaca
    # rebalance()

    # starting our main process
    start_loop()

# def rebalance():

#     positions = api.list_positions()
#     cash = account.cash

#     for position in positions:
#         # check if ticker is a currently held position
#             if position.symbol in tickers.keys():
#                 # calculate percentage of portfolio
#                 pop = math.floor(position.cost_basis / cash)
#                 # update this percentage to our ticker value, and warn user
#                 # if this conflicts with current desired pop
#                 if tickers.get(position.symbol) != pop:
#                     logging.warning("desired pop is {} while current is (and using) {}"
#                                     .format(tickers.get(position.symbol), pop))
#                 tickers[position.symbol] = pop
#                 #subtract from our total cash, to calculate new tickers later
#                 cash -= position.cost_basis

#     # now that we've allocated portfolio percentages for our existing positions,
#     # we can calculate new percentages for our new desired tickers
#     position_tickers = []
#     for p in positions = position_tickers.append(p.symbol)

#     for ticker in tickers.keys():
#         if ticker not in position_tickers:
#             pass
#             #take remaining

#     # percentage of portfolio
#     # pop = math.floor(100 * 1 / len(tickers))

def start_loop():
    logging.info("starting main loop")

    # populate processes list with an instance per ticker
    logging_queue = multiprocessing.Queue()
    for ticker in tickers:
        process = multiprocessing.Process(target=work, args=(logging_queue,ticker,))
        process.start()
        child_processes.append(process)

    # listen to any logging requests, and populate our log file using a mutex
    while True:
        log = logging_queue.get()
        if log['priority'] == 'debug': logging.debug(log['data'])
        if log['priority'] == 'info': logging.info(log['data'])
        if log['priority'] == 'warning': logging.warning(log['data'])
        if log['priority'] == 'error': logging.error(log['data'])
        if log['priority'] == 'critical': logging.critical(log['data'])
        logging_queue.task_done()

def work(logging_queue, ticker):
    # configure out logger to be global to this processes namespace
    global logger
    logger = logging_queue

    cash = 10000
    while True:
        try:
            # calling algorithms and using the last closing price
            macd_result = macd(ticker)['close']
            rsi_result = rsi(ticker)['close']
            cash = buy_or_sell_macd_rsi(macd_result, rsi_result, ticker, cash)
        except FunctionTimedOut:
            log("PID: {} TICKER: {} timed out! TIMEOUT = {}".format(os.getpid(), ticker, TIMEOUT), 'error')
            break
        
        # wait our desired amount of seconds (as per Alpaca)
        time.sleep(ALPACA_SLEEP_CYCLE)

    log("PID: {} TICKER: {} is exiting".format(os.getpid(), ticker))

@func_set_timeout(TIMEOUT)
def buy_or_sell_macd_rsi(macd_result, rsi_result, ticker, cash):
    # buy
    if macd_result > 0 and rsi_result < 40:
        order = api.submit_order(
            symbol=ticker,
            size='buy',
            type='market',
            qty=math.floor(cash / api.get_position(ticker).market_value),
            time_in_force='fok',
            extended_hours=true)
        if order.status == 'accepted':
            log("bought {} shares of {} at avg price of ${} for ${}!".format(
                order.qty, 
                ticker, 
                order.filled_avg_price,
                order.qty * order.filled_avg_price))
            cash = 0
        else:
            log("{} buy order was unable to be fulfilled! cash: {}".format(ticker, cash))

    #sell
    elif macd_result < 0 and rsi_result > 60:
        order_id = api.submit_order(
            symbol=ticker,
            size='sell',
            type='market',
            qty=api.get_position(ticker).qty,
            time_in_force='fok',
            extended_hours=true)
        if order.status == 'accepted':
            log("closed position for {}!".format(ticker))
            cash = order.qty * order.filled_avg_price
        else:
            log("{} sell order was unable to be closed! cash: {}".format(ticker, cash))
    else:
        log("{} -> macd: {}, rsi: {}. no trade signal thrown".format(ticker, macd_result, rsi_result), 'error')
    
    return cash

@func_set_timeout(TIMEOUT)
def macd(ticker):
    # setting time period to grab data (start doesn't matter)
    start = '1970-01-01'
    end = datetime.datetime.now()

    # calculate short-term EMA
    short_period = 12 # past 12 minutes
    short_data = api.polygon.historic_agg_v2(ticker, short_period, 'minute', _from=start, to=end).df
    short_ema = pandas.Series.ewm(short_data, span=short_period).mean().iloc[-1]

    # calculate long-term EMA
    long_period = 26 # past 26 mintues
    long_data = api.polygon.historic_agg_v2(ticker, long_period, 'minute', _from=start, to=end).df
    long_ema = pandas.Series.ewm(long_data, span=long_period).mean().iloc[-1]

    return short_ema - long_ema

@func_set_timeout(TIMEOUT)
def rsi(ticker):
    # setting time period to grab data (start doesn't matter)
    start = '1970-01-01'
    end = datetime.datetime.now()
    
    rsi_period = 14 # past 14 minutes

    # grab our ticker prices and grab only the deltas
    stock_data = api.polygon.historic_agg_v2(ticker, rsi_period, 'minute', _from=start, to=end).df
    delta = stock_data.diff()
    up, down = delta.copy(), delta.copy()
    
    # ignore all values unimportant to our delta direction
    up[up < 0] = 0
    down[down > 0] = 0

    # calculate the rolling means, and divide
    rolling_up = up.rolling(rsi_period).mean()
    rolling_down = down.rolling(rsi_period).mean().abs()

    # and finally, get our rsi
    rs = rolling_up / rolling_down
    rsi = 100.0 - (100.0 / (1.0 + rs))
    return rsi.iloc[-1]

def cleanup(*args):
    for process in child_processes:
        print("terminating process {}".format(process.pid))
        process.terminate()
    os._exit(0)

logger = None
def log(data, priority='info'):
    logger.put({'priority': priority, 'data': data})

for sig in (SIGABRT, SIGINT, SIGTERM):
    signal(sig, cleanup)

if __name__ == "__main__":
    try:
        main()
    finally:
        cleanup()