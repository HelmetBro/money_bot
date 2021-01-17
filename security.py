import logger
import math

import process_api

from func_timeout import func_set_timeout
TIMEOUT = 9

class Security:
    SECURITY_START_ALLOWANCE = 10000
    def __init__(self, ticker, allowance=SECURITY_START_ALLOWANCE):
        self.ticker    = ticker
        self.allowance = allowance
        self.position  = None

    @func_set_timeout(TIMEOUT)
    def buy_david_custom(self, upper_bound, lower_bound):
        if self.has_position():
            logger.log("position already exists with {} shares!".format(self.position.qty), 'debug')
            return
        # market orders are only avaliable during market hours
        order = process_api.api.submit_order(
            symbol=self.ticker,
            side='buy',
            type='limit',
            qty=self.max_buy_qty(), ###later need to consider updating allowance when a sell order executes
            limit_price=str(self.current_price()+0.01),
            time_in_force='gtc',
            order_class='bracket',
            take_profit={'limit_price': upper_bound},
            stop_loss={'stop_price': lower_bound})
        logger.log("submitted buy order for {} shares of {}!".format(
            order.qty, 
            self.ticker))

    @func_set_timeout(TIMEOUT)
    def buy(self):
        if self.has_position():
            logger.log("position already exists with {} shares!".format(self.position.qty), 'debug')
            return
        # market orders are only avaliable during market hours
        order = process_api.api.submit_order(
            symbol=self.ticker,
            side='buy',
            type='market',
            qty=self.max_buy_qty(), ###later need to consider updating allowance when a sell order executes
            time_in_force='fok')
        logger.log("submitted buy order for {} shares of {}!".format(
            order.qty, 
            self.ticker))

    @func_set_timeout(TIMEOUT)
    def sell(self):
        if not self.has_position():
            logger.log("no shares for ticker {} exist!".format(self.ticker), 'debug')
            return
        # never sell at a price lower than what was bought!
        if self.is_negative_profit():
            return
        # market orders are only avaliable during market hours
        order = process_api.api.submit_order(
                symbol=self.ticker,
                side='sell',
                type='market',
                qty=self.position.qty,
                time_in_force='fok')

        entry_price = float(self.position.avg_entry_price)
        sell_price  = self.current_price()
        logger.log("submitted sell order for {}! bought at ${} selling for ${} profit = ${}".format(
            self.ticker,
            entry_price,
            sell_price,
            sell_price - entry_price))

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

    def is_negative_profit(self):
        return float(self.position.avg_entry_price) >= self.current_price()

    @func_set_timeout(TIMEOUT)
    def has_position(self):
        try:
            self.position = process_api.api.get_position(self.ticker)
            return True
        except:
            return False