import pandas
import threading
import time

from logbook import Logger
from pylivetrader.api import order_target, record, symbol

BUY_AMOUNT = 100

log = Logger('algo-logger')

# called once when algo.py runs for the first time
def initialize(context):

    # list all tickers we want to trade, with their threads
    tickers = ['AAPL', 'MSFT', 'TSLA']

    # asset that we'll be trading.
    # context.asset = symbol('AAPL')

# called every time interval specified
def handle_data(context, data):

    # create a thread for each ticker (yes it must be created every time)
    
    # loop this
    # threading.Thread(target=)

    # macd = macd(context, data)

    # Trading logic
    if macd > 0:
        # order_target_percent allocates a specified percentage of your
        # portfolio to a long position in a given asset. (A value of 1
        # means that 100% of your portfolio will be allocated.)
        order_id = order_target(context.asset, BUY_AMOUNT)
        if order_id:
            log.info("Bought {} shares of {}".format(BUY_AMOUNT,
                                                     context.asset.symbol))
    elif macd < 0:
        # You can supply a negative value to short an asset instead.
        order_id = order_target(context.asset, 0)
        if order_id:
            log.info("Closed position for {}".format(context.asset.symbol))

    # Save values for later inspection
    record(AA=data.current(context.asset, 'price'),
           short_mavg=short_ema,
           long_mavg=long_ema)

def macd(context, data):

    # calculate short-term EMA
    order_target(context.asset, BUY_AMOUNT)
    short_periods = 12 # past 12 minutes
    short_data = data.history(
        context.asset, 'price', bar_count=short_periods, frequency="1m")
    short_ema = pandas.Series.ewm(short_data, span=short_periods).mean().iloc[-1]

    # calculate long-term EMA
    long_periods = 26 # past 26 mintues
    long_data = data.history(
        context.asset, 'price', bar_count=long_periods, frequency="1m")
    long_ema = pandas.Series.ewm(long_data, span=long_periods).mean().iloc[-1]

    return short_ema - long_ema