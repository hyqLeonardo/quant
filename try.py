# -*- coding:utf-8 -*-
from util_quant import *
import bcolz
import os

# csv_file = 'all.csv'
# with open(csv_file, 'wb') as csv_w:
# 	wr = csv.writer(csv_w, quoting=csv.QUOTE_ALL)
# 	wr.writerow(['股票代码', '公告标题', '公告链接', '日期'])

# df = pd.DataFrame(columns = ['股票代码'.decode('utf-8'), '公告标题'.decode('utf-8'), '公告链接'.decode('utf-8'), '日期'.decode('utf-8')])
# df['股票代码'.decode('utf-8')].astype(str)
# df = pd.read_csv('all.csv', dtype=str)
# if want to make the date as DataFrame index, do this
# df = pd.read_csv('all_ubuntu.csv', dtype=str, 
# 					index_col='日期', parse_dates=True,
# 					usecols=['股票代码', '公告标题', '公告链接', '日期'],
# 					na_values=['nan'])	
# print(df.head())
# date = df.ix[:, 3][0]
# print(date)
# print(type(date))
# d = datetime.strptime(date, '%Y-%m-%d %H:%M:%S')
# print(d)
# print(type(d))

def _p(file_name):
	path = './rqalpha/bundle/'
	return os.path.join(path, file_name)

def get_trading_date():
	f_name = 'trading_dates.bcolz'
	trading_dates = pd.Index(pd.Timestamp(str(d)) for d in bcolz.open(_p(f), 'r'))
	return trading_dates