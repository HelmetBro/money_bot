import process_api

def get(ticker, period, time_unit, start, end, data=None):
    if data != None: # then we must be backtrading
        
        return 
    else:
        return process_api.api.polygon.historic_agg_v2(ticker, period, time_unit, _from=start, to=end).df 
