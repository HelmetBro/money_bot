import datetime
import pandas
import alpaca_trade_api as tradeapi
api = tradeapi.REST()

import logger
from func_timeout import func_set_timeout, FunctionTimedOut

import process_api

TIMEOUT = 9

@func_set_timeout(TIMEOUT)
def buy_or_sell_macd_rsi(macd_result, rsi_result, security):
    if macd_result > 0 and rsi_result < 33.33:
        security.buy()
    elif macd_result < 0 and rsi_result > 66.66:
        security.sell()
    else:
        logger.log("{} -> macd: {}, rsi: {}. no trade signal thrown".format(security.ticker, macd_result, rsi_result), 'debug')

def macd(ticker):
    # setting time period to grab data (start doesn't matter)
    end = datetime.datetime.now()
    start = end - datetime.timedelta(hours=1)

    # calculate long-term EWM
    long_period = 26 # past 26 mintues
    long_data = process_api.api.polygon.historic_agg_v2(ticker, long_period, 'minute', _from=start, to=end).df
    if long_data.size < long_period:
        return 0
    long_ema = pandas.Series.ewm(long_data, span=long_period).mean().iloc[-1]

    # calculate short-term EWM
    short_period = 12 # past 12 minutes
    short_data = process_api.api.polygon.historic_agg_v2(ticker, short_period, 'minute', _from=start, to=end).df
    if short_data.size < short_period:
        return 0
    short_ema = pandas.Series.ewm(short_data, span=short_period).mean().iloc[-1]

    return short_ema - long_ema

def rsi(ticker):
    # setting time period to grab data (start doesn't matter)
    end = datetime.datetime.now()
    start = end - datetime.timedelta(hours=1)

    rsi_period = 14 # past 14 minutes

    # grab our ticker prices and grab only the deltas
    stock_data = process_api.api.polygon.historic_agg_v2(ticker, rsi_period, 'minute', _from=start, to=end).df
    if stock_data.size < rsi_period:
        return 50
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
