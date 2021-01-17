import datetime
import pandas
import data
import alpaca_trade_api as tradeapi
api = tradeapi.REST()

import logger
from func_timeout import func_set_timeout

import process_api

TIMEOUT = 9

@func_set_timeout(TIMEOUT)
def buy_and_sell_david_custom(ticker, start, end, data=None):
    # run both strats
    macd_result = macd(ticker, start, end, data)['close']
    rsi_result = rsi(ticker, start, end, data)['close']
    
    # get our bounds and submit our order
    upper_bound,lower_bound = get_std_from_ewm(ticker, start, end)
    macd_limit = -0.0014
    if macd_result > macd_limit and rsi_result < 30: #33.33:
        return 'buy_limit_stop',upper_bound,lower_bound # security.buy_david_custom(upper_bound, lower_bound)
    else:
        logger.log("{} -> macd: {}, rsi: {}. no trade signal thrown".format(ticker, macd_result, rsi_result), 'debug')

@func_set_timeout(TIMEOUT)
def buy_or_sell_macd_rsi(ticker, start, end, data=None):
    # run both strats
    macd_result = macd(ticker, start, end, data)['close']
    rsi_result = rsi(ticker, start, end, data)['close']
    
    # make a decision to buy/sell
    if macd_result > 0 and rsi_result < 33.33:
        return 'buy'
    elif macd_result < 0: # and rsi_result > 66.66:
        return 'sell'
    
    # if undesireable, don't make a decision
    logger.log("{} -> macd: {}, rsi: {}. no trade signal thrown".format(ticker, macd_result, rsi_result), 'debug')
    return 'none'

def get_std_from_ewm(ticker, start, end):
    #getting our data and calculating bounds from it
    history_df = data.get(ticker, 1, 'minute', start, end)
    upper = history_df['close'].ewm + history_df.std['close'] * 2
    lower = history_df['close'].ewm - history_df.std['close']
    return upper,lower

def macd(ticker, start, end, data):
    # calculate long-term EWM
    long_period = 26 # past 26 mintues
    long_data = data.get(ticker, long_period, 'minute', start, end, data)
    if long_data.size < long_period:
        return 0 # value that does not activate
    long_ema = pandas.Series.ewm(long_data, span=long_period).mean().iloc[-1]

    # calculate short-term EWM
    short_period = 12 # past 12 minutes
    short_data = data.get(ticker, short_period, 'minute', start, end, data)
    if short_data.size < short_period:
        return 0
    short_ema = pandas.Series.ewm(short_data, span=short_period).mean().iloc[-1]

    return short_ema - long_ema

def rsi(ticker, start, end, data):
    rsi_period = 14 # past 14 minutes

    # grab our ticker prices and grab only the deltas
    stock_data = data.get(ticker, rsi_period, 'minute', start, end, data)
    if stock_data.size < rsi_period:
        return 50 # value that does not activate
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
