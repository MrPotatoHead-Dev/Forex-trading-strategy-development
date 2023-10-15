import pandas as pd
from datetime import datetime
import datetime as dt
import time
import matplotlib.pyplot as plt
import warnings
from sklearn.preprocessing import StandardScaler
import seaborn as sns
import numpy as np
import copy

warnings.simplefilter("ignore")

# load dataframe
guWk = pd.read_csv("../GBPUSD60.csv")


def structureMT4Data(df):
    """Clean the data tha is supplied free from MT4 historical data centre.
    add some more columns including the pairs return
    :param df: (pd.Dataframe) that holds the OHCL values
    :return (pd.Dataframe)"""
    data = df
    data.columns = ["date", "time", "open", "high", "low", "close", "volume"]
    data["datetime"] = pd.to_datetime(data["date"] + " " + data["time"])
    data["date"] = pd.to_datetime(data["date"])
    data["date"] = pd.to_datetime(data["date"])

    data["week"] = data["date"].dt.isocalendar().week
    data["month"] = data["date"].dt.month
    data["quarter"] = data["date"].dt.quarter
    data["year"] = data["date"].dt.year

    data["return"] = ((data["close"] - data["open"]) / data["open"]) * 100
    data["h1_trend"] = data.apply(
        lambda row: 1 if row["close"] > row["open"] else 0, axis=1
    )
    data["pip_size_body"] = abs(data["open"] - data["close"]) * 10000
    data["pip_size_wick"] = abs(data["high"] - data["low"]) * 10000
    data.set_index("datetime", inplace=True)
    data["hour"] = df.index.hour
    df = df[df["high"] != df["low"]]

    data.dropna(inplace=True)
    data = data[data["year"] >= 2018]

    data = data[data["year"] < 2023]
    return data


df = structureMT4Data(guWk)


def dailyTrend(df):
    """add a column with the daily trend being bullish or bearish. 2 for bullish 1 for bearish"""
    data = df
    # resample the data to the daily timeframe
    dailydf = data.resample("D").agg(
        {"open": "first", "high": "max", "low": "min", "close": "last"}
    )
    # find the trend of the daily rows
    dailydf["daily_trend"] = dailydf.apply(
        lambda row: 1 if row["close"] > row["open"] else 0, axis=1
    )
    # merge daily data with hourly data
    data = data.merge(
        dailydf["daily_trend"], how="left", left_index=True, right_index=True
    )
    data = data.fillna(method="bfill", axis=0)
    data.dropna(inplace=True)
    return data


df = dailyTrend(df)


def statistics(df):
    """print results for the hours probability of being an up or down candle based off the daily trend"""
    data = df.copy()
    reduce_df = data[["h1_trend", "daily_trend", "hour"]]
    count_df = pd.DataFrame()

    for i in range(24):
        hour = i
        # find all the data based off the hour
        h1_rows = reduce_df[reduce_df["hour"] == i]

        row_df = pd.DataFrame()
        # seperate the based off the daily trend
        bull_days = h1_rows[h1_rows["daily_trend"] == 1.0]
        bear_days = h1_rows[h1_rows["daily_trend"] == 0.0]
        # find the total number of rows
        total = h1_rows.shape[0]
        up_total = bull_days.shape[0]
        dwn_total = bear_days.shape[0]
        # calculate the trend based off a percentage of total
        t_perc_bull = round((len(h1_rows[h1_rows["h1_trend"] == 1]) / total) * 100, 1)
        t_perc_bear = round((len(h1_rows[h1_rows["h1_trend"] == 0]) / total) * 100, 1)
        up_day_up_h1 = round(
            (len(bull_days[bull_days["h1_trend"] == 1]) / up_total) * 100, 1
        )
        up_day_dwn_h1 = round(
            (len(bull_days[bull_days["h1_trend"] == 0]) / up_total) * 100, 1
        )
        dwn_day_up_h1 = round(
            (len(bear_days[bear_days["h1_trend"] == 1]) / dwn_total) * 100, 1
        )
        dwn_day_dwn_h1 = round(
            (len(bear_days[bear_days["h1_trend"] == 0]) / dwn_total) * 100, 1
        )
        row_data = {
            "hour": i,
            "total_bull": t_perc_bull,
            "total_bear": t_perc_bear,
            "up_day_up_h1": up_day_up_h1,
            "up_day_dwn_h1": up_day_dwn_h1,
            "dwn_day_up_h1": dwn_day_up_h1,
            "dwn_day_dwn_h1": dwn_day_dwn_h1,
        }
        row_df = pd.DataFrame([row_data])
        count_df = pd.concat([count_df, row_df], ignore_index=True)
        # get the total sample size

    return count_df


def volatilityh1(df):
    """Find the average pip size of each candle to determine when the volatile times of the day are
    :param df: (pd.Dataframe) housing the OHCL values for a given pair"""
    hr_lst_body = []
    hr_lst_wicks = []
    for hr in range(24):
        hour = df[df["hour"] == hr]
        hr_lst_body.append(hour["pip_size_body"].mean())
        hr_lst_wicks.append(hour["pip_size_wick"].mean())
    return hr_lst_wicks, hr_lst_body


res_wick, res_body = volatilityh1(df)
y = [i for i in range(24)]

fig, ax = plt.subplots()
ax.plot(y, res_body, color="blue", label="Body")
ax.plot(y, res_wick, color="black", label="Wick")

ax.set_title("Average pip size of each hourly candle")
ax.axvline(x=9, color="r")
ax.axvline(x=15, color="r")

ax.legend()
plt.show()
"""plotting results"""
# bullish_days = df[df["daily_trend"] == 1.0]
# bearish_days = df[df["daily_trend"] == 0.0]
# # create a subplot that shows the return for hourly data under different market trends
# fig, axes = plt.subplots(3, 1)
# sns.boxplot(x="hour", y="return", data=df, whis=9, ax=axes[0])
# sns.boxplot(x="hour", y="return", data=bullish_days, whis=9, ax=axes[1])
# sns.boxplot(x="hour", y="return", data=bearish_days, whis=9, ax=axes[2])
# # plot title
# axes[0].set_title("Total")
# axes[1].set_title("Bullish days")
# axes[2].set_title("Bearish days")
# # plot session starts for London and New York
# axes[0].axvline(09.5, color=".3", dashes=(2, 2))
# axes[0].axvline(14.5, color=".3", dashes=(2, 2))
# axes[1].axvline(09.5, color=".3", dashes=(2, 2))
# axes[1].axvline(14.5, color=".3", dashes=(2, 2))
# axes[2].axvline(09.5, color=".3", dashes=(2, 2))
# axes[2].axvline(14.5, color=".3", dashes=(2, 2))

# plt.show()
