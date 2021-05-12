# what positions do I currently have?
# what positions am I asked to trade, and don't have?
# ^ take what those positions are, and divide by current cash.
# thats how much each position has. get the share price, divide by
# each positions alloted cash amount, and that's how much qty I'm going
# to be trading :)

# when a position sells, keep track of realized profit. if thats enough
# for a share, then add that to the qty that it should trade!

# # returns the investable cash for each ticker
# def calc_even_investing_cash(api, tickers):
#     positions = api.list_positions()
#     num_new_positions = len(tickers)
#     num_current_positions = len(positions)

#     # get all cash in the market (unrealized profits + invested)
#     total_invested = 0
#     for pos in positions:
#         # remove all existing tickers from "new tickers"
#         if pos.symbol in tickers:
#             num_new_positions -= 1

#         # if we have a position open already, add that to
#         # our tickers list to continue investing
#         else:
#             tickers.append(pos.symobl)

#         total_invested += pos.cost_basis;

#     cash = api.get_account().cash
#     return int(cash / (num_current_positions + num_current_positions))

def add_current_tickers(api, tickers):
    positions = api.list_positions()
    for pos in positions:
        if pos.symbol not in tickers:
            tickers.append(pos.symbol)
    return positions

def calc_investable_cash(cash, ticker, tickers, positions):
    for pos in positions:
        if ticker == pos.symbol:
            return 0

    num_new_positions = len(tickers) - len(positions)
    return int(cash / num_new_positions)