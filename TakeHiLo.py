import pandas as pd
from datetime import datetime
import datetime as dt
import time
import matplotlib.pyplot as plt
import warnings

warnings.simplefilter("ignore")

df_d = pd.read_csv("../GBPUSD1440.csv")
df_w = pd.read_csv("../GUWeekly.csv")
df_eu = pd.read_csv("../EURUSD1440.csv")
df_uc = pd.read_csv("../USDCAD1440.csv")

""" - calculates the percentage that a candle takes either the high or low of the previous candle
    - shows the amount of times each day of the week forms the high and low of multiple pairs"""


def structureMT4Data(df):  # df cleaning and formatting
    df.columns = ["date", "time", "open", "high", "low", "close", "volume"]
    df["date"] = pd.to_datetime(df["date"])
    df["date"] = pd.to_datetime(df["date"], format="%Y%m/%d")
    df["year"] = df["date"].dt.year
    df["day_month"] = df["date"].dt.strftime("%m/%d")
    df["day_of_week"] = df["date"].dt.day_name()

    df.set_index("date", inplace=True)
    return df


# structure the dataframes

df_daily = structureMT4Data(df_d)
df_eu = structureMT4Data(df_eu)
df_uc = structureMT4Data(df_uc)
df_weekly = structureMT4Data(df_w)

# reduce the dataframes to a certain year and above
date = "2010-01-01"
date_range_d = df_daily.index >= date
date_range_eu = df_eu.index >= date
date_range_uc = df_uc.index >= date
date_range_w = df_weekly.index >= date
df_daily = df_daily[date_range_d]
df_eu = df_eu[date_range_eu]
df_uc = df_uc[date_range_uc]

df_weekly = df_weekly[date_range_w]
df_weekly = df_weekly[df_weekly["time"] != "02:00"]


def insideCandleStats(df):
    """looks at the candle sticks to determain how often a candlestick takes the previous candlesticks high or low and looks at if inside candles have both their highs and lows taken
    :param df: (pd.Dataframe) for the OHCL values
    :return stats (List), insideCandle (List), insidesweep (List)"""
    stats = []
    insideSweep = []
    insideCandle = []
    for i in range(1, len(df) - 1):
        if df["high"].iloc[i] > df["high"].iloc[i - 1]:
            stats.append(1)
        elif df["low"].iloc[i] < df["low"].iloc[i - 1]:
            stats.append(-1)
        elif (
            df["low"].iloc[i] > df["low"].iloc[i - 1]
            and df["high"].iloc[i] < df["high"].iloc[i - 1]
        ):
            insideCandle.append(1)
            if (
                df["low"].iloc[i + 1] < df["low"].iloc[i]
                and df["high"].iloc[i + 1] > df["high"].iloc[i]
            ):
                insideSweep.append(1)
        elif (
            df["low"].iloc[i] < df["low"].iloc[i - 1]
            and df["high"].iloc[i] > df["high"].iloc[i - 1]
        ):
            stats.append(2)  # sweep both high and low of previous candle
        else:
            pass
    return stats, insideCandle, insideSweep


stats_d, insideCandle_d, insideSweep_d = insideCandleStats(df_daily)
stats_w, insideCandle_w, insideSweep_w = insideCandleStats(df_weekly)

eitherLoHiSweep_d = (len(stats_d) / len(df_daily)) * 100
print(f"Sample size: {len(df_daily)} daily candles")
print(f"Chance of high or low of pCandle taken: {round(eitherLoHiSweep_d,2)}%")
sweepHiLoInside_d = (len(insideSweep_d) / len(insideCandle_d)) * 100
print(f"Inside candles: {len(insideCandle_d)}")
print(
    f"Inside candle has high and low taken on the next candle: {round(sweepHiLoInside_d,2)}%"
)
print("#################################################################")
eitherLoHiSweep_w = (len(stats_w) / len(df_weekly)) * 100
print(f"Sample size: {len(df_weekly)} weekly candles")
print(f"Chance of high or low of pCandle taken: {round(eitherLoHiSweep_w,2)}%")
sweepHiLoInside_w = (len(insideSweep_w) / len(insideCandle_w)) * 100
print(f"Inside candles: {len(insideCandle_w)}")
print(
    f"Inside candle has high and low taken on the next candle: {round(sweepHiLoInside_w,2)}%"
)


# Finding the day the high or low of that week was formed
def highLowDoW(df):
    df = df[df["day_of_week"] != "Saturday"]
    high_day = df.resample("W")["high"].agg([("max_high", "idxmax")])
    low_day = df.resample("W")["low"].agg([("min_low", "idxmin")])

    # Combine the two series into a single dataframe
    high_low = pd.concat([high_day, low_day], axis=1)
    high_low["max_high"] = pd.to_datetime(high_low["max_high"], format="%Y%m/%d")
    high_low["min_low"] = pd.to_datetime(high_low["min_low"], format="%Y%m/%d")
    high_low["DoW_high"] = high_low["max_high"].dt.day_name()
    high_low["DoW_low"] = high_low["min_low"].dt.day_name()

    high_low["Bull or Bear"] = ""
    for i in range(len(high_low)):
        if high_low["max_high"].iloc[i] > high_low["min_low"].iloc[i]:
            high_low["Bull or Bear"].iloc[i] = "Bullish"
        else:
            high_low["Bull or Bear"].iloc[i] = "Bearish"

    bull_mask = high_low["Bull or Bear"] == "Bullish"
    bear_mask = high_low["Bull or Bear"] == "Bearish"

    # Use the boolean masks to select the rows with "Bullish" and "Bearish" labels
    bull_df = high_low.loc[bull_mask]
    bear_df = high_low.loc[bear_mask]

    # Print the resulting dataframes

    high_counts_overall = high_low["DoW_high"].value_counts()
    high_counts_bullish = bull_df["DoW_high"].value_counts()
    high_counts_bearish = bear_df["DoW_high"].value_counts()
    # Count the number of times each day of the week appears in the "DoW_low" column
    low_counts_overall = high_low["DoW_low"].value_counts()
    low_counts_bullish = bull_df["DoW_low"].value_counts()
    low_counts_bearish = bear_df["DoW_low"].value_counts()
    return (
        high_counts_overall,  # 0
        high_counts_bullish,  # 1
        high_counts_bearish,  # 2
        low_counts_overall,  # 3
        low_counts_bullish,  # 4
        low_counts_bearish,  # 5
    )


# Print the resulting counts
print("*************************************")
print("\nOverall results")
print("Highs by day of the week:")
print(highLowDoW(df_daily)[0])
print("\nLows by day of the week:")
print(highLowDoW(df_daily)[3])
print("\n*************************************")

print("\nBullish weeks results")
print("Highs by day of the week:")
print(highLowDoW(df_daily)[1])
print("\nLows by day of the week:")
print(highLowDoW(df_daily)[4])
print("\n*************************************")

print("\nBearish weeks results")
print("Highs by day of the week:")
print(highLowDoW(df_daily)[2])
print("\nLows by day of the week:")
print(highLowDoW(df_daily)[5])
print("*************************************")
print("******************EU*****************")
print("*************************************")
print("\nOverall results")
print("Highs by day of the week:")
print(highLowDoW(df_eu)[0])
print("\nLows by day of the week:")
print(highLowDoW(df_eu)[3])
print("\n*************************************")

print("\nBullish weeks results")
print("Highs by day of the week:")
print(highLowDoW(df_eu)[1])
print("\nLows by day of the week:")
print(highLowDoW(df_uc)[4])
print("\n*************************************")

print("\nBearish weeks results")
print("Highs by day of the week:")
print(highLowDoW(df_eu)[2])
print("\nLows by day of the week:")
print(highLowDoW(df_eu)[5])
print("*************************************")
print("******************UC*****************")
print("*************************************")
print("\nOverall results")
print("Highs by day of the week:")
print(highLowDoW(df_uc)[0])
print("\nLows by day of the week:")
print(highLowDoW(df_uc)[3])
print("\n*************************************")

print("\nBullish weeks results")
print("Highs by day of the week:")
print(highLowDoW(df_uc)[1])
print("\nLows by day of the week:")
print(highLowDoW(df_uc)[4])
print("\n*************************************")

print("\nBearish weeks results")
print("Highs by day of the week:")
print(highLowDoW(df_uc)[2])
print("\nLows by day of the week:")
print(highLowDoW(df_uc)[5])
print("*************************************")
