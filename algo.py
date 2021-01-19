import datetime
import pandas
import backend
import pytz

import logger
from func_timeout import func_set_timeout

TIMEOUT = 9

@func_set_timeout(TIMEOUT)
def buy_and_sell_david_custom(ticker, data=None):
    # run both strats
    macd_result = macd(ticker, data)
    rsi_result = rsi(ticker, data)

    # if we fail the algo's (can't pull enough data) then stop and return
    if macd_result == None or rsi_result == None: return

    macd_result = macd_result['close'] 
    rsi_result = rsi_result['close']
    
    std_period = 20
    # get our bounds, check if we have enough data already
    upper_bound,lower_bound = get_std_from_ewm(ticker, data, std_period) # uses last 20 minutes of data to calculate ewm
    if upper_bound == None or lower_bound == None:
        return
    
    macd_limit = -0.0014
    if macd_result > macd_limit and rsi_result < 30: #33.33:
        return 'buy_limit_stop',upper_bound,lower_bound # security.buy_david_custom(upper_bound, lower_bound)
    else:
        logger.log("{} -> macd: {}, rsi: {}. no trade signal thrown".format(ticker, macd_result, rsi_result), 'debug')

@func_set_timeout(TIMEOUT)
def buy_or_sell_macd_rsi(ticker, data=None):
    # run both strats
    macd_result = macd(ticker, data)
    rsi_result = rsi(ticker, data)

    # if we fail the algo's (can't pull enough data) then stop and return
    if macd_result == None or rsi_result == None: return

    macd_result = macd_result['close'] 
    rsi_result = rsi_result['close']
    
    # make a decision to buy/sell
    if macd_result > 0 and rsi_result < 33.33:
        return 'buy'
    elif macd_result < 0 and rsi_result > 66.66:
        return 'sell'
    
    # if undesireable, don't make a decision
    logger.log("{} -> macd: {}, rsi: {}. no trade signal thrown".format(ticker, macd_result, rsi_result), 'debug')
    return 'none'

def get_std_from_ewm(ticker, data, period, end_date=None, interval=1, timespan='minute'):
    # getting our data and calculating our bounds from it
    history_df = backend.get(ticker, period, interval, timespan, data)
    if len(history_df.index) < period:
        return None,None

    ewm = history_df['close'].ewm(period).mean().iloc[-1]
    upper = ewm + history_df['close'].std() * 2
    lower = ewm - history_df['close'].std()
    return upper,lower

def macd(ticker, data, end_date=None, interval=1, timespan='minute'):
    # calculate long-term EWM
    long_period = 26 # past 26 mintues
    long_data = backend.get(ticker, long_period, interval, timespan, data)
    if len(long_data.index) < long_period:
        return None
    long_ema = long_data.ewm(long_period).mean().iloc[-1]
    
    # calculate short-term EWM
    short_period = 12 # past 12 minutes
    short_data = backend.get(ticker, short_period, interval, timespan, data)
    if len(short_data.index) < short_period:
        return None
    short_ema = short_data.ewm(short_period).mean().iloc[-1]

    return short_ema - long_ema

def rsi(ticker, data, end_date=None, interval=1, timespan='minute'):
    rsi_period = 14 # past 14 minutes

    # grab our ticker prices and grab only the deltas
    stock_data = backend.get(ticker, rsi_period + 1, interval, timespan, data)
    if len(stock_data.index) < rsi_period + 1:
        return None
    delta = stock_data.diff()
    up,down = delta.copy(),delta.copy()
    
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