import multiprocessing
import logging
import time

import alpaca_trade_api as tradeapi
api = tradeapi.REST()

FORMAT = '%(asctime)-15s | %(message)s'
logging.basicConfig(format=FORMAT, filename='history.log', level=logging.INFO)

# account = api.get_account()
# account.status

tickers = ['AAPL', 'MSFT', 'TSLA']

# called once when algo.py runs for the first time
def initialize(context):

    start_loop(60)
    # asset that we'll be trading.
    # context.asset = symbol('AAPL')


def start_loop(seconds):
    
    # run our sub processes
    jobs = []
    run_workers(jobs)

    # wait our desired amount of seconds (as per Alpaca)
    sleep(seconds)

    # check if all our jobs finished successfully
    for job in jobs:
        if job.is_alive():
            logging.warning("Process {} is still alive! Killing it now".format(job.pid))
            job.terminate()

    # if still processes exist
        # log
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

    macd = macd(ticker)

    # combined trading logic
    if macd > 0:
        submit_order
        # order_id = order_target(context.asset, BUY_AMOUNT)
        if order_id:
            logging.info("Bought {} shares of {}".format(BUY_AMOUNT, context.asset.symbol))

    elif macd < 0:
        submit_order
        # order_id = order_target(context.asset, 0)
        if order_id:
            logging.info("Closed position for {}".format(context.asset.symbol))

    # don't forget to log

def macd(ticker):

    # calculate short-term EMA
    short_period = 12 # past 12 minutes
    short_data = api.polygon.historic_agg_v2(ticker, short_period, 'minute', _from=start, to=end).df
    short_ema = pandas.Series.ewm(short_data, span=short_periods).mean().iloc[-1]

    # calculate long-term EMA
    long_period = 26 # past 26 mintues
    long_data = api.polygon.historic_agg_v2(ticker, long_period, 'minute', _from=start, to=end).df
    long_ema = pandas.Series.ewm(long_data, span=long_periods).mean().iloc[-1]

    return short_ema - long_ema