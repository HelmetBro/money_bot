import process_api
import datetime
import pytz
import logger

def get(ticker, period, interval, timespan, data=None, end_date=None):
    start,end = get_time_periods(period * interval, end_date, timespan)
    if data != None: # then we must be backtrading
        return data 
    else:
        return process_api.api.polygon.historic_agg_v2(ticker, interval, timespan, _from=start, to=end, limit=period).df

### helper function
def get_time_periods(delta, end_date=None, timespan='minute'):
    end = end_date
    start = None
    if end_date == None:
        end = datetime.datetime.now(tz=pytz.timezone('US/Eastern'))
    # should try to use non-plural, as it's what Alpaca API uses
    if timespan == 'seconds' or timespan == 'second':
        start = end - datetime.timedelta(seconds=delta)
    if timespan == 'minutes' or timespan == 'minute':
        start = end - datetime.timedelta(minutes=delta)
    if timespan == 'hours' or timespan == 'hour':
        start = end - datetime.timedelta(hours=delta)
    if timespan == 'days' or timespan == 'day':
        start = end - datetime.timedelta(days=delta)
    if timespan == 'weeks' or timespan == 'week':
        start = end - datetime.timedelta(weeks=delta)
    return start,end