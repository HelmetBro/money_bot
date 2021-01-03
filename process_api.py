# Multiprocessing requires a new session to be created
# for every process. When forking, the existing session
# is duplicated and therefore uses the same session.
# this work-around creates a new session each time

# Alpaca api stuff
import alpaca_trade_api as tradeapi

def setup_api():
    global api
    api = tradeapi.REST()