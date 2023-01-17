import matplotlib.pyplot as plt

from datetime import datetime
from typing import List

from backend import Backend
from definitions import FilterOperator, FilterCondition, VisualizeFilters, \
    DefaultFieldNames, GameName, CustomFieldNames


backend = None

def parse_datetime_from_db(timestamp: str):
    return datetime.strptime(timestamp, "%Y-%m-%d")

def cumulative_sum_from_series(data: List):
    cumulative = []
    runSum = 0
    for d in data:
        runSum += d
        cumulative.append(runSum)
    return cumulative

"""
Plot cumulative value of data over time
data: List of (time, value) tuples
"""
def plot_cumulative(data: List[tuple]):
    time = [
        parse_datetime_from_db(d[0]) for d in data 
    ]
    values = [d[1] for d in data]
    plt.plot(time, cumulative_sum_from_series(values))
    plt.gcf().autofmt_xdate()
    plt.show()


def plot_all_time_winnings(_filter=VisualizeFilters({})):
    data = get_session_data(
        GameName.TEXAS_HOLDEM,
        [ DefaultFieldNames.DATE, DefaultFieldNames.NET_EARN, CustomFieldNames.CURRENCY ],
        _filter=_filter
    )
    data = sorted(data)
    
    rmbConversionRate = backend.get_rmb_conversion_rate()
    currencyConvertedData = [
        tuple([t[0], t[1] / (1 if t[2] == 'USD' else rmbConversionRate)]) for t in data
    ]
    plot_cumulative(currencyConvertedData)


"""
Plot summary stats
"""
def plot_all_time_stats(_filter=VisualizeFilters({})):
    data = get_session_data(
        GameName.TEXAS_HOLDEM,
        [ DefaultFieldNames.NET_EARN, CustomFieldNames.CURRENCY, CustomFieldNames.OCCASION, DefaultFieldNames.LENGTH ],
        _filter=_filter
    )

    rmbConversionRate = backend.get_rmb_conversion_rate()
    currencyConvertedData = [
        tuple([t[0] / (1 if t[1] == 'USD' else rmbConversionRate), t[2], t[3]]) for t in data
    ]

    # Print the overall and hourly breakdown by occasion
    # Data structure: {
    #     occasion1: {
    #         winning:
    #         timed_winning:
    #         hours:
    #     },
    #     ...
    # }
    occasion_template_dict = {
        'w': 0,
        't_w': 0,
        'h': 0,
    }
    all_occasion_summary = { 'Overall': dict(occasion_template_dict) }
    for net_earn, occasion, length in currencyConvertedData:
        if occasion not in all_occasion_summary:
            all_occasion_summary[occasion] = dict(occasion_template_dict)
        all_occasion_summary['Overall']['w'] += net_earn
        all_occasion_summary[occasion]['w'] += net_earn

        if length is not None:
            all_occasion_summary['Overall']['h'] += length
            all_occasion_summary['Overall']['t_w'] += net_earn
            all_occasion_summary[occasion]['h'] += length
            all_occasion_summary[occasion]['t_w'] += net_earn

    for occasion, summary in all_occasion_summary.items():
        print(occasion)
        print(f"  Total win: {summary['w']}")
        print(f"  Recorded hourly win: {summary['t_w']}/{summary['h']} = {summary['t_w']/summary['h'] if summary['h'] else 'no data'}")

def get_session_data(gameName: str, columns: List[str], _filter: VisualizeFilters):
    gameSessions = backend.get_sessions(gameName, _filter)
    rows = []
    for gameSession in gameSessions.values():
        sessionVals = gameSession.get_values()
        rows.append(tuple(sessionVals[c] if c in sessionVals else None for c in columns))
    return rows


def main():
    global backend
    backend = Backend()
    plot_all_time_stats()
    plot_all_time_winnings(
        _filter=VisualizeFilters({
            # DefaultFieldNames.TAGS: [
            #     FilterCondition(FilterOperator.CONTAINS, 'Purchase')
            # ],
            # CustomFieldNames.OCCASION: [
            #     FilterCondition(FilterOperator.EQUAL, 'Global')
            # ]
        })
    )



if __name__ == '__main__':
    main()