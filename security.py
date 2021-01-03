import logger

import process_api

from func_timeout import func_set_timeout, FunctionTimedOut
TIMEOUT = 9

class Security:
    SECURITY_START_ALLOWANCE = 10000
    def __init__(self, ticker, allowance=SECURITY_START_ALLOWANCE):
        self.ticker = ticker
        try:
            self.update()
        except:
            logger.log("no current position for {} in account".format(self.ticker))
            self.qty = 0
            self.allowance = allowance

    @func_set_timeout(TIMEOUT)
    def update(self):
        self.position = process_api.api.get_position(self.ticker)
        self.side = position.side
        self.qty = int(position.qty)
        self.allowance = float(position.cost_basis)
        logger.log("{} qty {}, side {}, allowance {}".format(self.ticker, self.qty, self.side, self.allowance), 'debug')

    @func_set_timeout(TIMEOUT)
    def current_price(self):
        try:
            market_value = float(process_api.api.get_position(self.ticker).current_price)
        except:
            logger.log("was not able to get last trade price of {}!".format(self.ticker), 'error')
            raise Exception

        return market_value
    
    def max_buy_qty():
        print("QTY {}".format(math.floor(security.allowance / self.current_price())))
        return math.floor(security.allowance / self.current_price())