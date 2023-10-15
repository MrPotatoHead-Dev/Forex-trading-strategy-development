import pandas as pd
from datetime import datetime
import datetime as dt
import time
import matplotlib.pyplot as plt
import warnings
from sklearn.preprocessing import StandardScaler
import plotly.graph_objects as go
import numpy as np

warnings.simplefilter("ignore")

df = pd.read_csv("../GBPUSD1440.csv")


def structureMT4Data(df, year):  # df cleaning and formatting
    """cleans the data that is retrieved from MT4 and adds columns for days of the week, month and year
    :param df: (pd.Dataframe) containing the OHCL data
    :param year: (int) removes all the data before that year
    :return (pd.Dataframe) updated data with datetime index"""
    df_copy = df.copy()
    df_copy.columns = ["date", "time", "open", "high", "low", "close", "volume"]

    df_copy["date"] = pd.to_datetime(df_copy["date"])
    df_copy.set_index(df_copy["date"], inplace=True)
    df_copy["DoW"] = df_copy["date"].dt.dayofweek

    df_copy["month"] = df_copy["date"].dt.month
    df_copy["year"] = df_copy["date"].dt.year
    # df.set_index("date", inplace=True)

    df_copy = df_copy[df_copy["high"] != df_copy["low"]]
    df_copy = df_copy[df_copy["year"] >= year]
    df_copy.dropna(inplace=True)
    return df_copy


def candle_trend(row):
    if row["close"] > row["open"]:
        return 1
    else:
        return -1


year = 2018
df = structureMT4Data(df, year)
df["trend"] = df.apply(lambda row: candle_trend(row), axis=1)


def addSwingPoints(df):
    df_copy = df.copy()
    df_copy["swing"] = None
    for i in range(1, len(df_copy) - 1):
        if (
            df_copy["high"].iloc[i - 1] < df_copy["high"].iloc[i]
            and df_copy["high"].iloc[i] > df_copy["high"].iloc[i + 1]
        ):  # swing high
            df_copy["swing"].iloc[i] = 1
        elif (
            df_copy["low"].iloc[i - 1] > df_copy["low"].iloc[i]
            and df_copy["low"].iloc[i] < df_copy["low"].iloc[i + 1]
        ):  # swing low
            df_copy["swing"].iloc[i] = -1
        else:
            df_copy["swing"].iloc[i] = 0
    df_copy = df_copy.dropna()
    return df_copy


df = addSwingPoints(df)
print(df)

""" weekly profiles to investigate
Bearish:
Monday high of the week, Thursday low of the week 
Monday high of the week, Friday low of the week 
Tuesday high of the week, Thursday low of the week 
Tuesday high of the week, Friday low of the week
Wednesday high of the week, Thursday low of the week
Wednesday high of the week, Friday low of the week

Anything else is considered an anomoly
"""


def plotprofile(weeks, high, low, code, side):
    """plot al the data for each profile
    :param weeks: (pd.Dataframe) containing the OHCL values
    :param high: (String) for which day was the high of the week
    :param low: (String) for which day was the low of the week
    :return saved plots to disk"""
    layout = go.Layout(autosize=False, width=1200, height=800)

    fig = go.Figure(
        data=go.Candlestick(
            x=weeks["date"],
            open=weeks["open"],
            high=weeks["high"],
            low=weeks["low"],
            close=weeks["close"],
        )
    )
    fig.update(layout_xaxis_rangeslider_visible=False, layout=layout)
    fig.update_xaxes(
        rangebreaks=[dict(bounds=["sat", "mon"])],
    )

    fig.write_image(f"gbp_{low}_{high}_{side}_{code}.png")


def weeklyProfiles(df, lookback):
    """Find the weeks where monday is the low of the week and friday is the high then save those plots straight to the file
    :param df: (pd.Dataframe) containg the OHCL data
    :param lookbac: (int) the amount of days to lookback to plot
    :return plots saved to folder"""
    indx = 1

    for i in range(len(df)):
        if df["DoW"].iloc[i] == 4:
            if i > 5:
                # slice the data frame into a single week
                week = df.iloc[i - 4 : i + 1]
                # find the index of the weekly high and low for that week
                min_index = week["low"].idxmin()
                min_row = week.loc[min_index]
                max_index = week["high"].idxmax()
                max_row = week.loc[max_index]
                # look for the
                if min_row["DoW"] == 0 and max_row["DoW"] == 4:
                    start_day = min_row["date"] - pd.DateOffset(days=lookback)
                    weeks = df[
                        (df["date"] >= start_day) & (df["date"] <= max_row["date"])
                    ]
                    plotprofile(weeks, "Fri", "Mon", indx, "bull")
                    indx += 1

                # Monday the low and Thursday is the high
                elif min_row["DoW"] == 0 and max_row["DoW"] == 3:
                    # Monday is the low (+1 to lookback)
                    start_day = min_row["date"] - pd.DateOffset(days=lookback)
                    # thursday is the high (+1 to get Friday)
                    end_day = max_row["date"] + pd.DateOffset(days=1)
                    weeks = df[(df["date"] >= start_day) & (df["date"] <= end_day)]
                    plotprofile(weeks, "Thu", "Mon", indx, "bull")
                    indx += 1
                # Tuesday the low and Friday is the high
                elif min_row["DoW"] == 1 and max_row["DoW"] == 4:
                    # tuesday is the low (+1 to lookback)
                    start_day = min_row["date"] - pd.DateOffset(days=lookback + 1)
                    # Friday is the high (+1 to get Friday)
                    end_day = max_row["date"]
                    weeks = df[(df["date"] >= start_day) & (df["date"] <= end_day)]
                    plotprofile(weeks, "Fri", "Tue", indx, "bull")
                    indx += 1
                # Tuesday the low and Thursday is the high
                elif min_row["DoW"] == 1 and max_row["DoW"] == 3:
                    # Tuesday is the low (+1 to lookback)
                    start_day = min_row["date"] - pd.DateOffset(days=lookback + 1)
                    # Thursday is the high (+1 to get Friday)
                    end_day = max_row["date"] + pd.DateOffset(days=1)
                    weeks = df[(df["date"] >= start_day) & (df["date"] <= end_day)]
                    plotprofile(weeks, "Thu", "Tue", indx, "bull")
                    indx += 1
                # Wednesday the low and Friday is the high
                elif min_row["DoW"] == 2 and max_row["DoW"] == 4:
                    # Wednesday is the low (+2 to lookback)
                    start_day = min_row["date"] - pd.DateOffset(days=lookback + 2)
                    # Friday is the high
                    end_day = max_row["date"]
                    weeks = df[(df["date"] >= start_day) & (df["date"] <= end_day)]
                    plotprofile(weeks, "Fri", "Wed", indx, "bull")
                    indx += 1
                # Wednesday the low and Thursday is the high
                elif min_row["DoW"] == 2 and max_row["DoW"] == 3:
                    # Wednesday is the low (+2 to lookback)
                    start_day = min_row["date"] - pd.DateOffset(days=lookback + 2)
                    # Thursday is the high
                    end_day = max_row["date"] + pd.DateOffset(days=1)
                    weeks = df[(df["date"] >= start_day) & (df["date"] <= end_day)]
                    # plot results
                    plotprofile(weeks, "Thu", "Wed", indx, "bull")
                    # update index
                    indx += 1
                #################################### Bearish weeks ####################################
                elif max_row["DoW"] == 0 and min_row["DoW"] == 4:
                    start_day = max_row["date"] - pd.DateOffset(days=lookback)
                    weeks = df[
                        (df["date"] >= start_day) & (df["date"] <= min_row["date"])
                    ]
                    plotprofile(weeks, "Mon", "Fri", indx, "bear")
                    indx += 1

                # Monday the low and Thursday is the high
                elif max_row["DoW"] == 0 and min_row["DoW"] == 3:
                    # Monday is the low (+1 to lookback)
                    start_day = max_row["date"] - pd.DateOffset(days=lookback)
                    # thursday is the high (+1 to get Friday)
                    end_day = min_row["date"] + pd.DateOffset(days=1)
                    weeks = df[(df["date"] >= start_day) & (df["date"] <= end_day)]
                    plotprofile(weeks, "Mon", "Thu", indx, "bear")
                    indx += 1
                # Tuesday the low and Friday is the high
                elif max_row["DoW"] == 1 and min_row["DoW"] == 4:
                    # tuesday is the low (+1 to lookback)
                    start_day = max_row["date"] - pd.DateOffset(days=lookback + 1)
                    # Friday is the high (+1 to get Friday)
                    end_day = min_row["date"]
                    weeks = df[(df["date"] >= start_day) & (df["date"] <= end_day)]
                    plotprofile(weeks, "Tue", "Fri", indx, "bear")
                    indx += 1
                # Tuesday the low and Thursday is the high
                elif max_row["DoW"] == 1 and min_row["DoW"] == 3:
                    # Tuesday is the low (+1 to lookback)
                    start_day = max_row["date"] - pd.DateOffset(days=lookback + 1)
                    # Thursday is the high (+1 to get Friday)
                    end_day = min_row["date"] + pd.DateOffset(days=1)
                    weeks = df[(df["date"] >= start_day) & (df["date"] <= end_day)]
                    plotprofile(weeks, "Tue", "Thu", indx, "bear")
                    indx += 1
                # Wednesday the low and Friday is the high
                elif max_row["DoW"] == 2 and min_row["DoW"] == 4:
                    # Wednesday is the low (+2 to lookback)
                    start_day = max_row["date"] - pd.DateOffset(days=lookback + 2)
                    # Friday is the high
                    end_day = min_row["date"]
                    weeks = df[(df["date"] >= start_day) & (df["date"] <= end_day)]
                    plotprofile(weeks, "Wed", "Fri", indx, "bear")
                    indx += 1
                # Wednesday the low and Thursday is the high
                elif max_row["DoW"] == 2 and min_row["DoW"] == 3:
                    # Wednesday is the low (+2 to lookback)
                    start_day = max_row["date"] - pd.DateOffset(days=lookback + 2)
                    # Thursday is the high
                    end_day = min_row["date"] + pd.DateOffset(days=1)
                    weeks = df[(df["date"] >= start_day) & (df["date"] <= end_day)]
                    # plot results
                    plotprofile(weeks, "Thu", "Wed", indx, "bear")
                    # update index
                    indx += 1


weeklyProfiles(df, 20)
