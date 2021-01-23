import backtrader_setup
import backend_data
import logger
from func_timeout import func_set_timeout

TIMEOUT = 9

@func_set_timeout(TIMEOUT)
def buy_and_sell_david_custom(security, trader=None):
    # run both strats
    macd_result = macd(security.ticker)['close']
    rsi_result = rsi(security.ticker)['close']

    # get our bounds, check if we have enough data already
    std_period = 20
    upper_bound,lower_bound = get_std_from_ewm(security.ticker, std_period) # uses last 20 minutes of data to calculate ewm
    if upper_bound == None or lower_bound == None: return

    # make a decision to buy/sell
    macd_limit = -0.0014
    if macd_result > macd_limit and rsi_result < 33.33:
        return security.buy_david_custom(upper_bound,lower_bound, trader)
    
    logger.log("{} -> macd: {}, rsi: {}. no trade signal thrown".format(security.ticker, macd_result, rsi_result), 'debug')

@func_set_timeout(TIMEOUT)
def buy_or_sell_macd_rsi(security):
    # run both strats
    macd_result = macd(security.ticker)['close'] 
    rsi_result = rsi(security.ticker)['close'] 

    # make a decision to buy/sell
    if macd_result > 0 and rsi_result < 33.33:
        security.buy()
    elif macd_result < 0 and rsi_result > 66.66:
        security.sell()
    
    # if undesireable, don't make a decision
    logger.log("{} -> macd: {}, rsi: {}. no trade signal thrown".format(security.ticker, macd_result, rsi_result), 'debug')

def get_std_from_ewm(ticker, period, interval=1, timespan='minute'):
    # getting our data and calculating our bounds from it
    history_df = backend_data.get(ticker, period, interval, timespan)
    if len(history_df.index) < period:
        raise Exception("insufficient data [std upper/lower]")  

    ewm = history_df['close'].ewm(period).mean().iloc[-1]
    upper = ewm + history_df['close'].std() * 2
    lower = ewm - history_df['close'].std()
    return upper,lower

def macd(ticker, interval=1, timespan='minute'):
    # calculate long-term EWM
    long_period = 26 # past 26 mintues
    long_data = backend_data.get(ticker, long_period, interval, timespan)
    if len(long_data.index) < long_period:
        raise Exception("insufficient data [macd long]")
    long_ema = long_data.ewm(long_period).mean().iloc[-1]
    
    # calculate short-term EWM
    short_period = 12 # past 12 minutes
    short_data = backend_data.get(ticker, short_period, interval, timespan)
    if len(short_data.index) < short_period:
        raise Exception("insufficient data [macd short]")
    short_ema = short_data.ewm(short_period).mean().iloc[-1]

    return short_ema - long_ema

def rsi(ticker, interval=1, timespan='minute'):
    rsi_period = 14 # past 14 minutes

    # grab our ticker prices and grab only the deltas
    stock_data = backend_data.get(ticker, rsi_period + 1, interval, timespan)
    if len(stock_data.index) < rsi_period + 1:
        raise Exception("insufficient data [rsi]")
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