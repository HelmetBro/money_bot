import logger
from func_timeout import func_set_timeout

# @func_set_timeout(TIMEOUT)
# def buy_and_sell_david_custom(events):
#     # run both strats
#     macd_signal_result = macd_with_signal(security.ticker)['close']
#     rsi_result = rsi(security.ticker)['close']

#     # get our bounds, check if we have enough data already
#     std_period = 20
#     std = std_from_ewm(security.ticker, std_period) # uses last 20 minutes of data to calculate ewm
#     if std is None: return

#     # make a decision to buy/sell
#     macd_signal_limit = -0.0014
#     if macd_signal_result > macd_signal_limit and rsi_result < 30: #33.33:
#         return security.buy_david_custom(std, trader)

#     logger.log("{} -> macd_signal: {}, rsi: {} so no trade signal thrown".format(
#         security.ticker, macd_signal_result, rsi_result), 'debug')

# def std_from_ewm(ticker, period, interval=1, timespan='minute'):
#     # getting our data and calculating our bounds from it
#     history_df = backend_data.get(ticker, period, interval, timespan)
#     if len(history_df.index) < period:
#         raise Exception("insufficient data [std upper/lower]")

#     # ewm = history_df['close'].ewm(period).mean().iloc[-1]
#     # upper = ewm + history_df['close'].std() * 2
#     # lower = ewm - history_df['close'].std()
#     return history_df['c'].std()

def macd_with_signal(long_data, short_data, ema_period):
    # calculate long-term EWM
    long_ema = long_data.ewm(len(long_data.index), adjust=False).mean().iloc[-1]

    # calculate short-term EWM
    short_ema = short_data.ewm(len(short_data.index), adjust=False).mean().iloc[-1]

    # macd line. this is to be compared to signal line
    macd = short_ema - long_ema

    # this calculates our signal line
    signal = macd.ewm(span=ema_period, adjust=False).mean()

    return macd - signal

def rsi(data):
    rsi_period = len(data.index) - 1
    # grab our ticker prices and grab only the deltas
    delta = data.diff()
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