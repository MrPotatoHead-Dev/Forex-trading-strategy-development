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
eu = pd.read_csv("../GBPUSD15_dirty.csv")
euhour = pd.read_csv("../GBPUSD60.csv")
""" This looks at how the m15 candlesticks form inside the 1h candlesticks"""


def structureMT4Data(df, year=2018):  # df cleaning and formatting
    df.columns = ["date", "time", "open", "high", "low", "close", "volume"]
    df["datetime"] = pd.to_datetime(df["date"] + " " + df["time"])
    df["date"] = pd.to_datetime(df["date"])
    df["date"] = pd.to_datetime(df["date"], format="%Y%m/%d")

    df["week"] = df["date"].dt.isocalendar().week
    df["month"] = df["date"].dt.month
    df["quarter"] = df["date"].dt.quarter
    df["year"] = df["date"].dt.year

    df["return"] = ((df["close"] - df["open"]) / df["open"]) * 100
    df.set_index("datetime", inplace=True)
    df["hour"] = df.index.hour
    df["minute"] = df.index.minute
    df = df[df["high"] != df["low"]]

    df["trend_min"] = df.apply(
        lambda row: 1 if row["close"] > row["open"] else 0, axis=1
    )
    df["trend_min"] = df["trend_min"].astype(int)
    df["hi-lo"] = (df["high"] - df["low"]) * 10000

    df.dropna(inplace=True)
    df = df[df["year"] >= year]

    return df


eu = structureMT4Data(eu, 2021)

# Seperate the given hours into blocks of time. i.e London, NY


def block_time(df, start_time, end_time):
    block = df.between_time(start_time, end_time)
    return block


london_start = "08:00"
london_end = "14:00"

ny_start = "15:00"
ny_end = "23:00"


def add_hourly_trend(df):
    hourly_candles = df.resample("1H").agg(
        {
            "open": "first",
            "high": "max",
            "low": "min",
            "close": "last",
        }
    )

    hourly_candles["trend_hr"] = hourly_candles.apply(
        lambda row: 1 if row["close"] > row["open"] else 0, axis=1
    )
    hourly_candles["trend_hr"] = hourly_candles["trend_hr"].astype(float)
    df = df.merge(
        hourly_candles["trend_hr"], how="left", left_index=True, right_index=True
    )

    df = df.fillna(method="ffill", axis=0)
    return df


eu = add_hourly_trend(eu)
ldn = block_time(eu, london_start, london_end)
ny = block_time(eu, ny_start, ny_end)


bullish_eu = ny[ny["trend_hr"] == 1]
bearish_eu = ny[ny["trend_hr"] == 0]


def avg_return_block(df, col1):
    avg = df.groupby("minute")[col1].mean()
    return avg


print(ldn)
# avg return
rtrn = "return"
avg_total_r = avg_return_block(ny, rtrn)
avg_bull_r = avg_return_block(bullish_eu, rtrn)
avg_bear_r = avg_return_block(bearish_eu, rtrn)

# high low
hilo = "hi-lo"
avg_total_hilo = avg_return_block(ny, hilo)
avg_bull_hilo = avg_return_block(bullish_eu, hilo)
avg_bear_hilo = avg_return_block(bearish_eu, hilo)


fig, ((ax1, ax2, ax3), (ax4, ax5, ax6)) = plt.subplots(2, 3)
x = [0, 15, 30, 45]
ax1.plot(x, avg_total_hilo, marker="o")
ax2.plot(x, avg_bull_hilo, marker="o")
ax3.plot(x, avg_bear_hilo, marker="o")


ax4.plot(x, avg_total_r, marker="o", color="r")
ax5.plot(x, avg_bull_r, marker="o", color="r")
ax6.plot(x, avg_bear_r, marker="o", color="r")


ax1.set_title("Total")
ax2.set_title("Bullish")
ax3.set_title("Bearish")
ax1.set_ylabel("High-Low", fontweight="bold", rotation=45)
ax4.set_ylabel("Return", fontweight="bold", rotation=45)


for ax in (ax1, ax2, ax3, ax4, ax5, ax6):
    ax.set_xticks(x)
    ax.set_xticklabels(x)
    ax.grid()


plt.show()
