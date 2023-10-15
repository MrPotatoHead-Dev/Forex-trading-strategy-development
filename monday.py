import pandas as pd
from datetime import datetime
import datetime as dt
import time
import matplotlib.pyplot as plt
import warnings

warnings.simplefilter("ignore")


""" Testing ADR on your favourte forex pairs"""

# import pair
gu = pd.read_csv("../GBPUSD1440.csv")


year = 2022


def structureMT4Data(df, date=2022):
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


df = structureMT4Data(gu)
# calulate the difference between the high and the low, and the open and close, in pips
df["bVolume"] = abs((df["open"] - df["close"]) * 10000)
df["cVolume"] = abs((df["high"] - df["low"]) * 10000)
df["trend"] = df.apply(
    lambda row: "Bullish" if row["close"] > row["open"] else "Bearish", axis=1
)

# investigate adr of both volumes
# look back factor (3, 5, ... days)
factor = 4
volume = 100
# empty lists
b_stats = []
c_stats = []
mon_trend_stats = []
for i in range(factor, len(df)):
    b_adr = df["bVolume"].iloc[i - factor : i].mean()
    c_adr = df["cVolume"].iloc[i - factor : i].mean()

    # retrieve ADR statistics
    if df["bVolume"].iloc[i] < b_adr:
        b_stats.append(0)
    elif df["bVolume"].iloc[i] > b_adr:
        b_stats.append(1)
    if df["cVolume"].iloc[i] < c_adr:
        c_stats.append(0)
    elif df["cVolume"].iloc[i] > c_adr:
        c_stats.append(1)

    # Thursday and friday are trending days
    if df["DoW"].iloc[i] == "Monday":
        if (
            df["DoW"].iloc[i - 2] == "Thursday"
            and df["DoW"].iloc[i - 1] == "Friday"
            and df["trend"].iloc[i - 2] == df["trend"].iloc[i - 1]
        ):
            vol = df["cVolume"].iloc[i - 2] + df["cVolume"].iloc[i - 1]

            if vol > volume:
                # if monday is a continuation day or not
                if df["trend"].iloc[i] == df["trend"].iloc[-1]:
                    mon_trend_stats.append(1)
                else:
                    mon_trend_stats.append(0)


b_less = b_stats.count(0)
b_more = b_stats.count(1)
c_less = c_stats.count(0)
b_perc = int(b_less / len(b_stats) * 100)
c_perc = int(c_less / len(c_stats) * 100)
print(
    f" bodys greater than ADR(3): {b_stats.count(1)}, less than: {b_stats.count(0)}, \n As aprecentage: {b_perc}%"
)
print(
    f" candles greater than ADR(3): {c_stats.count(1)}, less than: {c_stats.count(0)}, \n As a percentage: {c_perc}%"
)
mon_contiue = mon_trend_stats.count(1)
mon_reversal = mon_trend_stats.count(0)
mon_perc = round(mon_reversal / len(mon_trend_stats) * 100, 0)
print(
    f"If Thursday and Friday are trending days with a combined volume range of {volume}"
)
print(
    f"Monday Reverses: {mon_reversal}, Continues: {mon_contiue}, \n As a percentage {mon_perc}%"
)
