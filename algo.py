import multiprocessing
import logging
import time
import math
import datetime

import alpaca_trade_api as tradeapi
api = tradeapi.REST()
account = api.get_account()

FORMAT = '%(asctime)-15s | %(message)s'
logging.basicConfig(format=FORMAT, filename='history.log', level=logging.INFO)

tickers = {
    # symbol : desired percentage of portfolio
    'AAPL': 33,
    'TSLA': 34,
    'SBUX': 33}

def main():
    # ensuring our account setup is okay
    account_status = "account status: {}".format(account.status)
    print(account_status)
    logging.info(account_status)

    # check if tickers are tradable on Alpaca

    # 
    # rebalance()

    # starting our main process
    #start_loop(60)

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

def start_loop(seconds):
    
    logging.info("starting main loop")

    # run our sub processes
    jobs = []
    run_workers(jobs)

    # wait our desired amount of seconds (as per Alpaca)
    sleep(seconds)

    # check if all our jobs finished, and done successfully
    for job in jobs:
        if job.is_alive():
            api.cancel_all_orders()
            logging.warning("process {} is still alive! Canceling all orders and killing it now".format(job.pid))
            job.terminate()

    if status == 'failed':
        pass
        # log

def run_workers(jobs):

    # populate processes list with an instance per ticker
    for ticker in tickers:
        process = multiprocessing.Process(target=work, args=(ticker,))
        process.start()
        job.append(process)

def work(ticker):

    # calling algorithms using the closing price
    macd = macd(ticker)['close']
    rsi = rsi(ticker)['close']

    # buy
    if macd > 0 and rsi < 40:
        order_id = api.submit_order(
            symbol=ticker,
            size='buy',
            type='market',
            qty='100',
            time_in_force='fok',
            extended_hours=true) # temporary
        if order_id:
            logging.info("bought {} shares of {}".format(BUY_AMOUNT, context.asset.symbol))
        # else
        #     cancel_order(order_id)
        #     logging.warning("unable to buy {} shares of {}".format(BUY_AMOUNT, context.asset.symbol))
    
    #sell
    elif macd < 0 and rsi > 60:
        order_id = api.submit_order(
            symbol=ticker,
            size='sell',
            type='market',
            qty='100',
            time_in_force='fok',
            extended_hours=true) # temporary
        if order_id:
            logging.info("closed position for {}".format(context.asset.symbol))
        # else
        #     cancel_order(order_id)
        #     logging.info("unable to close position for {}".format(context.asset.symbol))

    # don't forget to log

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
    return rsi

if __name__ == "__main__":
    main()