import backtrader
import process_api
import datetime
import pytz
import backtrader_setup

def get(ticker, period, interval, timespan):
    # if we're backtrading, we already have set start/end dates. just return what we already computed
    if backtrader_setup.BACKTRADER:
        return backtrader_setup.data_frame[0:period]

    start,end = get_time_periods(period * interval, timespan)
    return process_api.api.polygon.historic_agg_v2(ticker, interval, timespan, _from=start, to=end, limit=period).df

### helper function
def get_time_periods(delta, timespan='minute'):
    end = datetime.datetime.now(tz=pytz.timezone('US/Eastern'))
    start = None
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