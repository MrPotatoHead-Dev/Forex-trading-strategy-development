import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import time


# upload and format data
data = pd.read_csv("../GBPUSD15_dirty.csv")

data.columns = ["date", "time", "open", "high", "low", "close", "volume"]
data["datetime"] = data["date"] + " " + data["time"]
data["date"] = pd.to_datetime(data["date"])
data["time"] = pd.to_datetime(data["time"], format="%H:%M").dt.time
data["datetime"] = pd.to_datetime(data["datetime"])
data["DoW"] = data["date"].dt.day_name()


data.set_index("datetime", inplace=True)
data["DoW"] = data.index.dayofweek

# reduce dataset to greater than 2015
start_date = "01-01-2022"
data = data[data["date"] > start_date]
print(data)
# asian session end and length
asia_start = datetime.strptime("03:00:00", "%H:%M:%S").time()
asia_end = datetime.strptime("07:00:00", "%H:%M:%S").time()

ldn_end = datetime.strptime("15:00:00", "%H:%M:%S").time()
asia_length = 16


def seekAndDestroy(data, asia_end, asia_length):
    asia_max = 10
    asia_min = 0
    seek_low = 0
    seek_high = 0
    asia_high = []
    asia_low = []
    seek_hi_lo = []
    seek_lo_hi = []
    date_sad = []
    for i in range(len(data)):
        if data["time"].iloc[i] == asia_end:
            # find the high and low of the asian session
            asia_max = data["high"].iloc[i - asia_length : i].max()
            asia_min = data["low"].iloc[i - asia_length : i].min()
            asia_mid = (asia_max + asia_min) / 2

        # check if the high of asia is swept and that the low has not been taken
        if data["high"].iloc[i] > asia_max and seek_high != 1:
            asia_high.append(data["time"].iloc[i])
            # switch on to see if low is also taken
            seek_low = 1
            # print(data["date"].iloc[i])
        # check if low is taken and that the high has not been taken
        elif data["low"].iloc[i] < asia_min and seek_low != 1:
            asia_low.append(data["time"].iloc[i])
            seek_high = 1

        # does it seek the low after the high?
        if seek_high == 1 and data["high"].iloc[i] > asia_max:
            seek_lo_hi.append((data["date"].iloc[i]))
            date_sad.append(data["date"].iloc[i])
            asia_max = 10

        elif seek_low == 1 and data["low"].iloc[i] < asia_min:
            # print(f'BEAR: {data["low"].iloc[i]} < {asia_min} \n asia high: {asia_max}')
            seek_hi_lo.append((data["date"].iloc[i]))
            date_sad.append(data["date"].iloc[i])
            asia_min = 0

        if data["time"].iloc[i] >= ldn_end and data["time"].iloc[i] < asia_start:
            asia_max = 10
            asia_min = 0
            seek_high = 0
            seek_low = 0
    return seek_hi_lo, seek_lo_hi, date_sad


seek_hi_lo, seek_lo_hi, date_sad = seekAndDestroy(data, asia_end, asia_length)
hi_lo = len(pd.Series(seek_hi_lo))
lo_hi = len(pd.Series(seek_lo_hi))
print(f"high to low: {hi_lo}, low to high: {lo_hi}")
sad_count = hi_lo + lo_hi
sample_size = len((data["date"]).value_counts())
proba = (sad_count / sample_size) * 100

print(proba)
