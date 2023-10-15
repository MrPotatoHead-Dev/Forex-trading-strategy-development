import pandas as pd
from datetime import datetime
import datetime as dt
import time
import matplotlib.pyplot as plt
import warnings

warnings.simplefilter("ignore")

# import pairs
gu = pd.read_csv("../GBPUSD1440.csv")

# gold = pd.read_csv("../XAUUSD1440.csv")

date = 2015


def structureMT4Data(df, date=date):
    """structure .csv file to datetime index as well as adding new columns for more information on the date, as well as the trend of the candle
    :param df: (pd.Dataframe) OHCL values that was downloaded from the MT4 platform
    :param date: (int) the starting year to pull information from
    :returns (pd.Dataframe)"""
    df.columns = ["date", "time", "open", "high", "low", "close", "volume"]

    df["date"] = pd.to_datetime(df["date"])
    df["date"] = pd.to_datetime(df["date"], format="%Y%m/%d")
    df["time"] = pd.to_datetime(df["time"], format="%H:%M").dt.time
    df["month"] = df["date"].dt.month
    df["year"] = df["date"].dt.year
    df["DoW"] = df["date"].dt.day_name()

    df.set_index("date", inplace=True)

    df = df[df["high"] != df["low"]]
    df = df.drop(["time", "volume"], axis="columns")
    df = df[df["year"] >= date]
    df = df[df["DoW"] != "Sunday"]
    df = df[df["DoW"] != "Saturday"]

    df.dropna(inplace=True)
    return df


gu = structureMT4Data(gu)
high_day = pd.DataFrame()
low_day = pd.DataFrame()
high_day = gu.resample("M")["high"].agg([("high_date", "idxmax")])
low_day = gu.resample("M")["low"].agg([("low_date", "idxmin")])


high_day["month"] = high_day["high_date"].dt.month
high_day["year"] = high_day["high_date"].dt.year
high_day["DoW"] = high_day["high_date"].dt.day_name()
high_day["DoM"] = high_day["high_date"].dt.day


low_day["month"] = low_day["low_date"].dt.month
low_day["year"] = low_day["low_date"].dt.year
low_day["DoW"] = low_day["low_date"].dt.day_name()
low_day["DoM"] = low_day["low_date"].dt.day
high_low = pd.merge(high_day, low_day, on=["month", "year"], suffixes=("_high", "_low"))
high_low["bull_bear"] = ""

for i in range(len(high_low)):
    if high_low["DoM_high"].iloc[i] > high_low["DoM_low"].iloc[i]:
        high_low["bull_bear"].iloc[i] = "bullish"
    else:
        high_low["bull_bear"].iloc[i] = "bearish"


bull_mnth = high_low[high_low["bull_bear"] == "bullish"]
bear_mnth = high_low[high_low["bull_bear"] == "bearish"]
print(bear_mnth)
low_counts_bearish = bear_mnth["DoM_low"].value_counts()
low_counts_bearish.columns = ["DoM", "count"]
high_counts_bearish = bear_mnth["DoM_high"].value_counts()
print(high_counts_bearish, low_counts_bearish)
