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


def get_session_data(gameName: str, columns: List[str], _filter: VisualizeFilters):
    gameSessions = backend.get_sessions(gameName, _filter)
    columnVals = {
        col: [] for col in columns
    }

    for session in gameSessions.values():
        sessionVals = colVal = session.get_values()
        for column in columns:
            colVal = sessionVals[column] if column in sessionVals else None
            columnVals[column].append(colVal)
    return [columnVals[col] for col in columns]


def main():
    global backend
    backend = Backend()
    data = get_session_data(
        GameName.TEXAS_HOLDEM,
        [ DefaultFieldNames.DATE, DefaultFieldNames.NET_EARN, CustomFieldNames.CURRENCY ],
        _filter=VisualizeFilters({
        })
    )
    tupledData = sorted(list(zip(*data)))
    
    rmbConversionRate = backend.get_rmb_conversion_rate()
    currencyConvertedData = []
    for t in tupledData:
        if t[2] == 'USD':
            currencyConvertedData.append((t[0], t[1]))
        elif t[2] == 'RMB':
            currencyConvertedData.append((t[0], t[1] / rmbConversionRate))
    plot_cumulative(currencyConvertedData)


if __name__ == '__main__':
    main()