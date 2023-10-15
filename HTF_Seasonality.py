import pandas as pd
from datetime import datetime
import datetime as dt
import time
import matplotlib.pyplot as plt
import warnings
from sklearn.preprocessing import StandardScaler
import seaborn as sns
import numpy as np

warnings.simplefilter("ignore")

# load dataframe
guWk = pd.read_csv("../GUWeekly.csv")
ucadWk = pd.read_csv("../USDCADweekly.csv")
euWk = pd.read_csv("../EURUSD10080.csv")
auWk = pd.read_csv("../AUDUSD10080.csv")
ftse = pd.read_csv("FTSE_clean.csv")
ten_year = "2013-01-01"
five_year = "2018-01-01"
two_year = "2020-01-01"


def structureMT4Data(df):
    """structure .csv file to datetime index as well as adding new columns for more information on the date, as well as the trend of the candle
    :param df: (pd.Dataframe) OHCL values that was downloaded from the MT4 platform
    :param date: (int) the starting year to pull information from
    :returns (pd.Dataframe)"""
    df.columns = ["date", "time", "open", "high", "low", "close", "volume"]

    df["date"] = pd.to_datetime(df["date"])
    df["date"] = pd.to_datetime(df["date"], format="%Y%m/%d")
    df["month"] = df["date"].dt.month
    df["quarter"] = df["date"].dt.quarter
    df["year"] = df["date"].dt.year

    df["return"] = ((df["close"] - df["open"]) / df["open"]) * 100
    # df.set_index("date", inplace=True)

    df = df[df["high"] != df["low"]]

    df.dropna(inplace=True)
    df = df[df["year"] < 2023]
    return df


def addFTSEonly(df):
    """Changing I have done to suit ftse pair"""
    df["date"] = pd.to_datetime(df["date"])
    df["date"] = pd.to_datetime(df["date"], format="%Y%m/%d")

    df.set_index("date", inplace=True)

    df["month"] = df.index.month
    df["quarter"] = df.index.quarter
    df["year"] = df.index.year
    df["return"] = ((df["close"] - df["open"]) / df["open"]) * 100
    df.dropna(inplace=True)

    return df


col = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "May",
    "Jun",
    "Jul",
    "Aug",
    "Sep",
    "Oct",
    "Nov",
    "Dec",
]


def avg_close(df, year=2013):
    df = df[df["year"] >= year]
    df = df[df["year"] < 2023]
    avg_month = []
    for i in range(1, 13):
        months = df[df["month"] == i]
        months_avg = months["close"].mean()
        avg_month.append(months_avg)

    avg_month = pd.DataFrame(data={"month": col, "avg": avg_month}, index=col)

    return avg_month


def hi_lo_avg(df, year=ten_year):
    date_range = df["year"] >= year
    df = df[date_range]
    df = df[df["year"] < 2023]
    avg_month = []
    for i in range(1, 13):
        months = df[df["month"] == i]
        months_avg = ((months["high"] + months["low"]) / 2).mean()
        avg_month.append(months_avg)
    avg_month = pd.DataFrame(data={"month": col, "avg": avg_month}, index=col)

    return avg_month


"""'
    high + low / 2
    open + close /2
"""


def scale_data(data):
    scaler = StandardScaler()
    data = data.to_numpy()
    data = data.reshape(-1, 1)
    normalized_data = scaler.fit(data)
    normalized_data = scaler.transform(data)
    return normalized_data


def quarter_return(df, year=2018):
    date_range = df["year"] >= year
    df = df[date_range]

    try:
        df.set_index("date", inplace=True)
    except KeyError:
        pass
    quarterly = df.resample("Q").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}
    )
    quarterly["quarter"] = quarterly.index.quarter
    _q_return = []

    for i in range(1, 5):
        quarter = quarterly[quarterly["quarter"] == i]
        _return = ((quarter["close"] - quarter["open"]).mean()) * 10000
        _q_return.append(_return)
    _col = ["Q1", "Q2", "Q3", "Q4"]
    quarter = pd.DataFrame(data={"Q": _col, "return": _q_return}, index=_col)
    return quarter


""" *************************************************
                 Code starts here
    ************************************************* """

currency_list = [guWk, euWk, auWk, ucadWk]
pair_label = ["GBPUSD", "EURUSD", "AUDUSD", "USDCAD"]
label = 0
for pair in currency_list:
    df = structureMT4Data(pair)

    year_15 = avg_close(df, 2008)
    year_5 = avg_close(df, 2018)
    year_2 = avg_close(df, 2020)

    year_10hl = hi_lo_avg(df, 2013)
    year_5hl = hi_lo_avg(df, 2018)
    year_2hl = hi_lo_avg(df, 2020)

    q_return = quarter_return(df)

    # # Plot seasonality
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(8, 9))
    ax.plot(year_15.index, scale_data(year_15["avg"]), label="15yr")
    ax.plot(year_5.index, scale_data(year_5["avg"]), label="5yr")
    ax.plot(year_2.index, scale_data(year_2["avg"]), label="2yr")
    ax.set_title(f"{pair_label[label]} Seasonality")
    ax.legend()
    ax.grid()

    ax2.bar(range(1, 5), q_return["return"])
    ax2.set_title("Quarterly Returns")
    ax2.grid(visible=False)
    ax2.set_xticks(range(1, 5), q_return["Q"])

    plt.show()

    df = df[df["year"] > 2018]
    sns.boxplot(x="quarter", y="return", data=df)

    plt.show()
    label = label + 1
