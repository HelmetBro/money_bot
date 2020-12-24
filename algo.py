import multiprocessing
import logging
import time
import math

import alpaca_trade_api as tradeapi
api = tradeapi.REST()
account = api.get_account()

# import order_wrapper as order

FORMAT = '%(asctime)-15s | %(message)s'
logging.basicConfig(format=FORMAT, filename='history.log', level=logging.INFO)

tickers = {
    # symbol : desired percentage of portfolio
    'AAPL': 50,
    'TSLA': 20,
    'MSFT': 30}

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

def rebalance():

    positions = account.list_positions()
    cash = account.cash

    for position in positions:
        # check if ticker is a currently held position
            if position.symbol in tickers.keys():
                # calculate percentage of portfolio
                pop = math.floor(position.cost_basis / cash)
                # update this percentage to our ticker value, and warn user
                # if this conflicts with current desired pop
                if tickers.get(position.symbol) != pop:
                    logging.warning("desired pop is {} while current is (and using) {}"
                                    .format(tickers.get(position.symbol), pop))
                tickers[position.symbol] = pop
                #subtract from our total cash, to calculate new tickers later
                cash -= position.cost_basis

    # now that we've allocated portfolio percentages for our existing positions,
    # we can calculate new percentages for our new desired tickers
    for ticker in tickers.keys():
        if ticker not in position:
            pass

    # percentage of portfolio
    pop = math.floor(100 * 1 / len(tickers))

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
            logging.warning("process {} is still alive! Canceling orders and killing it now".format(job.pid))
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

    macd = macd(ticker)

    # buy
    if macd > 0:
        order_id = api.submit_order(ticker, BUY_AMOUNT)
        if order_id:
            logging.info("bought {} shares of {}".format(BUY_AMOUNT, context.asset.symbol))
        # else
        #     pass
            #error
    #sell
    elif macd < 0:
        order_id = api.submit_order(ticker, BUY_AMOUNT)
        if order_id:
            logging.info("closed position for {}".format(context.asset.symbol))
        # else
        #     pass
            #error

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

if __name__ == "__main__":
    main()