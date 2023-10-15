import pandas as pd
from datetime import datetime
import datetime as dt
import time
import matplotlib.pyplot as plt
import warnings

warnings.simplefilter("ignore")
# df = pd.read_csv("GBPUSD30.csv")
gu15min = pd.read_csv("../GBPUSD15_dirty.csv")
eu15min = pd.read_csv("../EURUSD15.csv")
au15min = pd.read_csv("../AUDUSD15.csv")
ucad15min = pd.read_csv("../USDCAD15.csv")
uchf15min = pd.read_csv("../USDCHF15.csv")
uj15min = pd.read_csv("../USDJPY15.csv")
gold15min = pd.read_csv("../XAUUSD15.csv")
silver15min = pd.read_csv("../XAGUSD15.csv")


# session times
asian_session_finish = datetime.strptime("07:15:00", "%H:%M:%S").time()
london_session_start = datetime.strptime("08:15:00", "%H:%M:%S").time()
london_session_finish = datetime.strptime("15:15:00", "%H:%M:%S").time()
ny_session_start = datetime.strptime("15:00:00", "%H:%M:%S").time()
ny_session_finish = datetime.strptime("22:00:00", "%H:%M:%S").time()
year = 2020


def structureMT4Data(df, year=2018):  # df cleaning and formatting
    df.columns = ["date", "time", "open", "high", "low", "close", "volume"]
    df["datetime"] = pd.to_datetime(df["date"] + " " + df["time"])
    df["date"] = pd.to_datetime(df["date"])
    df["date"] = pd.to_datetime(df["date"], format="%Y%m/%d")
    df["time"] = pd.to_datetime(data["time"], format="%H:%M").dt.time

    df["week"] = df["date"].dt.isocalendar().week
    df["month"] = df["date"].dt.month
    df["quarter"] = df["date"].dt.quarter
    df["year"] = df["date"].dt.year

    df.set_index("datetime", inplace=True)
    df.dropna(inplace=True)
    df = df[df["year"] >= year]

    return df


# df["datetime"] = pd.to_datetime(df["datetime"], unit="ms").astype("datetime64[ns]")


def dailyHiLo(df):
    """finds the times where the highs and lows were formed throughout the day
    :param df: (pd.Dataframe) containing OHCL values
    :returns (pd.Series) counts of the consequtive times where highs and lows where formed
    """
    candle_count = 0
    daily_high_times = []
    daily_low_times = []
    day_counter = 0
    for i in range(1, len(df)):
        if df.date.iloc[i] != df.date.iloc[i - 1]:
            day_counter = day_counter + 1
            if candle_count >= 90:
                daily_high = max(df["high"].iloc[i - candle_count : i], default=0)
                daily_low = min(df["low"].iloc[i - candle_count : i], default=0)
                time_window = df["time"].iloc[i - candle_count : i]

                for index_high, value_high in enumerate(
                    df["high"].iloc[i - candle_count : i]
                ):
                    if value_high == daily_high and index_high != 0:
                        daily_high_times.append(time_window[index_high])
                for index_low, value_low in enumerate(
                    df["low"].iloc[i - candle_count : i]
                ):
                    if value_low == daily_low and index_low != 0:
                        daily_low_times.append(time_window[index_low])

            candle_count = 0
        candle_count = candle_count + 1

    combined_counts = lst2df(
        daily_high_times, daily_low_times, "daily_highs", "daily_lows"
    )
    return combined_counts


def rangedHiLo(df, time_finish, range_counnt, col1, col2):
    """this function finds the times a low and high was formed inside a timed range
    :param df: (pd.Dataframe) containging OHCL values
    :param timed_finish: (datetime object): the finishing time of the given range
    :param range_count: (int) number of candles inside the given range
    :param col1: (string) column name
    :param col2: (string) column name"""
    high_time = []
    low_time = []
    for i in range(len(df)):
        if df["time"].iloc[i] == time_finish:
            timed_range = df.iloc[i - range_counnt : i]
            timed_high = timed_range["high"].max()
            timed_low = timed_range["low"].min()

            for indx, val in timed_range.iterrows():
                if indx != 0:
                    if val["high"] == timed_high and indx.time() < time_finish:
                        high_time.append(indx.time())
                    elif val["low"] == timed_low and indx.time() < time_finish:
                        low_time.append(indx.time())
    counts = lst2df(high_time, low_time, col1, col2)
    return counts


def lst2df(lst1, lst2, col1, col2):
    """Takes in 2 lists full of times and finds the value counts for them
    :param lst1: (List) times where the highs were formed
    :param lst2: (List) times where the lows were formed
    :param col1: (string) column name
    :param col2: (string) column name
    returns pd.Series"""
    high_counts = pd.Series(lst1).value_counts()
    high_counts = high_counts.sort_index()
    low_counts = pd.Series(lst2).value_counts()
    low_counts = low_counts.sort_index()
    combined_counts = pd.concat([high_counts, low_counts], axis=1)
    combined_counts.columns = [col1, col2]
    return combined_counts


dfs = [gu15min, eu15min, au15min, ucad15min, uchf15min, uj15min, gold15min, silver15min]
# dfs = [gu15min, eu15min]
results = pd.DataFrame()
number = 0

for i, data in enumerate(dfs):
    df_cleaned = structureMT4Data(data)

    daily_res = dailyHiLo(df_cleaned)
    asia_res = rangedHiLo(
        df_cleaned, asian_session_finish, 18, "asia_highs", "asia_lows"
    )
    london_res = rangedHiLo(
        df_cleaned, london_session_finish, 26, "london_highs", "london_lows"
    )
    ny_res = rangedHiLo(df_cleaned, ny_session_finish, 29, "ny_highs", "ny_lows")
    results = pd.concat(
        [results, daily_res, asia_res, london_res, ny_res],
        axis=1,
    )
    labels = ["GU", "EU", "AU", "UCAD", "UCHF", "UJ", "Gold", "Silver"]
    label = labels[i]
    print(label)
    fig, ax = plt.subplots(figsize=(15, 8))
    daily_res = daily_res[1:-1]
    daily_res.plot(kind="bar", ax=ax, stacked=True)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

    plt.savefig(f"Daily_{label}_{year}.png")

    fig, ax = plt.subplots(figsize=(15, 8))
    asia_res = asia_res[1:-1]
    asia_res.plot(kind="bar", ax=ax, stacked=True)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

    plt.savefig(f"asia_res_{label}_{year}.png")

    fig, ax = plt.subplots(figsize=(15, 8))
    london_res = london_res[1:-1]
    london_res.plot(kind="bar", ax=ax, stacked=True)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

    plt.savefig(f"london_res_{label}_{year}.png")

    fig, ax = plt.subplots(figsize=(15, 8))
    ny_res = ny_res[2:-1]
    ny_res.plot(kind="bar", ax=ax, stacked=True)
    ax.set_xticklabels(ax.get_xticklabels(), rotation=45)

    plt.savefig(f"ny_res_{labels[i]}_{year}.png")
