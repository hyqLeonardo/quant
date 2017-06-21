import sys
import random
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from pandas.tseries.offsets import *
import datetime
import csv

## helper functions
# keep only year and moth(year-month) as string of datetime object
# return example: 2017-01-01
def date2ym_str(date):
    y = date.year
    m = date.month
    ym = '{}-{}'.format(y, m)
    return ym

def date2ymd_str(date):
    y = date.year
    m = date.month
    d = date.day
    ymd = '{}-{}-{}'.format(y, m, d)
    return ymd

def datetime2date(date_time):
	y = date_time.year
	m = date_time.month
	d = date_time.day
	return datetime.date(y, m, d)

def adjust_to_trading_date(date_time, trading_dates_list):
	''' trading_dates_list is a list of string indicate date
	'''
	ymd_str = date2ymd_str(date_time)

	if ymd_str in trading_dates_list:	# this date is trading date
		if date_time.hour >= 15:	# event should be in next day
			return get_next_trading_date(ymd_str)
		else: # return date as datetime.date() type
			return datetime2date(date_time)
	else: # this date is not trading day, return next trading day
		return get_next_trading_date(ymd_str)

# def shift_date(date, days):
# 	days_adjust = days + (days / 5) * 2
# 	return date + days_adjust * BDay()

# # pad series to a specific length
# def pad_series(series, length, aft=True):
# 	row_num = series.shape[0]
# 	if aft:	# pad for prices after SD
# 		new_index = range(row_num)
# 		pad_index = range(length)
# 	else:	# pad for prices before SD
# 		new_index = range(1 - row_num, 1)
# 		pad_index = range(-(length - 1), 1)

# 	series.index = new_index
# 	return series.reindex(pad_index)

# # compute return rate based on price series
# def price_to_rate(series, aft=True):
# 	length = series.shape[0]
# 	if aft:
# 		for d in range(length):
# 			series.iloc[length-1-d] = series.iloc[length-1-d]/series.iloc[0]-1
# 	else:
# 		for d in range(length):
# 			series.iloc[d] = series.iloc[d]/series.iloc[length-1]-1
# 	return series