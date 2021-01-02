import datetime
import pandas
import alpaca_trade_api as tradeapi
api = tradeapi.REST()

import logger
from func_timeout import func_set_timeout, FunctionTimedOut

TIMEOUT = 9

@func_set_timeout(TIMEOUT)
def buy(security):
    if security.qty > 0:
        logger.log("position already exists with {} shares".format(security.qty), 'debug')
        return

    # market orders are only avaliable during market hours
    order = api.submit_order(
        symbol=security.ticker,
        side='buy',
        type='market',
        qty=security.max_buy_qty(),
        time_in_force='ioc') # look into this later
    if order.status == 'accepted':
        security.update()
        logger.log("bought {} shares of {} at avg price of ${} for ${}!".format(
            security.qty, 
            ticker, 
            order.filled_avg_price,
            security.allowance))
    else:
        logger.log("{} buy order was unable to be fulfilled!".format(security.ticker))

@func_set_timeout(TIMEOUT)
def sell(security):
    if security.qty == 0:
        logger.log("no shares for ticker {} exist!".format(security.ticker), 'debug')
        return

    order_id = api.submit_order(
            symbol=security.ticker,
            side='sell',
            type='market',
            qty=str(security.qty),
            time_in_force='ioc')
    if order.status == 'accepted':
        security.update()
        logger.log("closed position for {}!".format(security.ticker))
    else:
        logger.log("{} sell order was unable to be closed!".format(security.ticker))

@func_set_timeout(TIMEOUT)
def buy_or_sell_macd_rsi(macd_result, rsi_result, security):
    if macd_result > 0 and rsi_result < 40:
        buy(security)
    elif macd_result < 0 and rsi_result > 60:
        sell(security)
    else:
        logger.log("{} -> macd: {}, rsi: {}. no trade signal thrown".format(security.ticker, macd_result, rsi_result), 'debug')

def macd(ticker):
    # setting time period to grab data (start doesn't matter)
    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=1)

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
    end = datetime.datetime.now()
    start = end - datetime.timedelta(days=1)

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