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
eu = pd.read_csv("../EURUSD1440.csv")
gu = pd.read_csv("../GBPUSD1440.csv")
ucad = pd.read_csv("../USDCAD1440.csv")
gold = pd.read_csv("../XAUUSD1440.csv")
nas = pd.read_csv("../NAS1001440.csv")
# starting year
year = 2018


# Cleaning and formatting data extracted from MT4's historical centre
def structureMT4Data(df, date=2018):
    """structure .csv file to datetime index as well as adding new columns for more information on the date, as well as the trend of the candle
    :param df: (pd.Dataframe) OHCL values that was downloaded from the MT4 platform
    :param date: (int) the starting year to pull information from
    :returns (pd.Dataframe)"""
    df.columns = ["date", "time", "open", "high", "low", "close", "volume"]

    df["date"] = pd.to_datetime(df["date"])
    df["date"] = pd.to_datetime(df["date"])
    df["time"] = pd.to_datetime(df["time"], format="%H:%M").dt.time
    df["month"] = df["date"].dt.month
    df["year"] = df["date"].dt.year
    df["num_day"] = df["date"].dt.dayofweek
    df["DoW"] = df["date"].dt.day_name()

    df["daily_trend"] = df.apply(
        lambda row: 1 if row["close"] > row["open"] else 0, axis=1
    )

    df.set_index("date", inplace=True)

    df = df[df["high"] != df["low"]]
    df = df.drop(["time", "volume"], axis="columns")
    df = df[df["year"] >= date]
    df = df[df["DoW"] != "Sunday"]
    df = df[df["DoW"] != "Saturday"]

    df.dropna(inplace=True)
    return df


# add the weekly trend to the daily data
def weekly_trend(df):
    """add the weekly trend to the daily dataframe in its own column
    :param df: (pd.dataframe) with OHCL values
    :returns (pd.Dataframe)"""
    weekly = df.resample("W-FRI").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}
    )
    weekly["weekly_trend"] = weekly.apply(
        lambda row: 1 if row["close"] > row["open"] else 0, axis=1
    )
    df = df.merge(weekly["weekly_trend"], how="left", left_index=True, right_index=True)
    df = df.fillna(method="bfill", axis=0)

    # find weekly high and low
    high_day = df.resample("W")["high"].agg([("max_high", custom_idxmax)])
    low_day = df.resample("W")["low"].agg([("min_low", custom_idxmin)])
    high_day["week_high"] = 1
    low_day["week_low"] = 1
    high_day.reset_index(drop=True, inplace=True)
    low_day.reset_index(drop=True, inplace=True)
    high_day.set_index("max_high", inplace=True)
    low_day.set_index("min_low", inplace=True)
    # add notation to the daily dataframe
    df = df.merge(high_day["week_high"], how="left", left_index=True, right_index=True)
    df = df.merge(low_day["week_low"], how="left", left_index=True, right_index=True)
    return df


# create the statistics on the daily trends in total, bullish and bearish weeks
def statistics(df):
    """seperates the bullish and bearish weeks to find the percentages of each day of the week closes above or below the open
    :param df: (pd.Dataframe)"""
    for i in range(0, 5, 1):
        day_of_week = df[df["num_day"] == i]
        day = day_of_week["DoW"].iloc[1]
        bull = day_of_week[day_of_week["daily_trend"] == 1]
        bear = day_of_week[day_of_week["daily_trend"] == 0]
        bull = bull.shape[0]
        bear = bear.shape[0]
        total = bull + bear
        bull_percent = (bull / total) * 100
        bear_percent = (bear / total) * 100
        print(day, f"{bull_percent:.0f}%", f"{bear_percent:.0f}%")


def weekly_hilo(df):
    df["week_high"] = df.apply(
        lambda row: row["DoW"] if row["week_high"] == 1.0 else 0, axis=1
    )
    df["week_low"] = df.apply(
        lambda row: row["DoW"] if row["week_low"] == 1.0 else 0, axis=1
    )
    return df


def run_multiple_pairs(df):
    df = structureMT4Data(df)
    df_w = weekly_trend(df)

    # seperate bullish and bearish weeks
    bull_weeks = df_w[df_w["weekly_trend"] == 1]
    bear_weeks = df_w[df_w["weekly_trend"] == 0]
    # combine the dataframes to loop through them at once
    scinarios = [df, bull_weeks, bear_weeks]
    # add a title to the results
    title = ["Total", "Bullish weeks", "Bearish bearish"]
    dot = 0
    for scinario in scinarios:
        print(title[dot])
        statistics(scinario)
        print("")
        dot = dot + 1

    # print highs and lows in bullish and bearish weeks
    print("")
    print("Bullish Weeks")
    trend = weekly_hilo(bull_weeks)
    print("High formed")
    print(trend["week_high"].value_counts())
    print("*" * 25)
    print("Low formed")
    print(trend["week_low"].value_counts())
    print("")

    print("Bearish Weeks")
    trend = weekly_hilo(bear_weeks)
    print("High formed")
    print(trend["week_high"].value_counts())
    print("*" * 25)
    print("Low formed")
    print(trend["week_low"].value_counts())
    print("")


def custom_idxmax(series):
    if not series.empty:
        return series.idxmax()
    else:
        return None


def custom_idxmin(series):
    if not series.empty:
        return series.idxmin()
    else:
        return None


# pairs used
pairs = [eu, gu, ucad, gold, nas]
labels = ["EURUSD", "GBPUSD", "USDCAD", "GOLD", "NAS"]
label = 0

# Loop through all the pairs
for pair in pairs:
    print(labels[label])
    run_multiple_pairs(pair)

    label = label + 1
