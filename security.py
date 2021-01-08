import logger
import math

import process_api

from func_timeout import func_set_timeout, FunctionTimedOut
TIMEOUT = 9

class Security:
    SECURITY_START_ALLOWANCE = 10000
    def __init__(self, ticker, allowance=SECURITY_START_ALLOWANCE):
        self.ticker = ticker
        self.allowance = allowance

    @func_set_timeout(TIMEOUT)
    def buy(self):
        if self.has_position():
            logger.log("position already exists with {} shares!".format(self.qty), 'debug')
            return
        # market orders are only avaliable during market hours
        order = process_api.api.submit_order(
            symbol=self.ticker,
            side='buy',
            type='market',
            qty=self.max_buy_qty(), #later need to consider updating allowance when a sell order executes
            time_in_force='fok')
        logger.log("submitted buy order for {} shares of {} at avg price of ${}!".format(
            order.qty, 
            self.ticker, 
            order.filled_avg_price))

    @func_set_timeout(TIMEOUT)
    def sell(self):
        if not self.has_position():
            logger.log("no shares for tick er {} exist!".format(self.ticker), 'debug')
            return
        # market orders are only avaliable during market hours
        order = process_api.api.submit_order(
                symbol=self.ticker,
                side='sell',
                type='market',
                qty=self.position.qty,
                time_in_force='fok')
        logger.log("submitted sell order for {}!".format(self.ticker))

    @func_set_timeout(TIMEOUT)
    def current_price(self):
        try:
            market_value = float(process_api.api.get_last_quote(self.ticker).askprice)
        except:
            logger.log("was not able to get last trade price of {}!".format(self.ticker), 'error')
            raise Exception

        return market_value
    
    def max_buy_qty(self):
        return math.floor(self.allowance / self.current_price())

    def has_position(self):
        try:
            self.position = process_api.api.get_position(self.ticker)
            return True
        except:
            return False