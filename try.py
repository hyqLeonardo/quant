# -*- coding:utf-8 -*-
from util_quant import *

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

def filter_title(title):
	if '投资者' in title:
		return True

def complete_code(code):

	if len(code) < 6: # code is empty or length smaller than 6
		return False
	elif code[:3] in ['600', '601']: # 上证
		return code + '.XSHG'
	elif code[:3] == '000': # 深证
		return code + '.XSHE'
	else: # neither
		return False

def announce2event(file_name):

	# read csv file into dataframe
	df = pd.read_csv(file_name, dtype=str,
					index_col='日期', parse_dates=True,
					usecols=['股票代码', '公告标题', '公告链接', '日期'],
					na_values=['nan'])

	# get date range
	start_date = date2ymd_str(df.index[-1])
	end_date = date2ymd_str(df.index[0])
	# index of event df, type: datetime.date, keep only trading dates
	index = get_trading_dates(start_date, end_date)
	# column of event df, 上证A股指数 + 深证A股指数
	# columns = index_components('000001.XSHG').extend(index_components('399107.XSHE'))
	columns = ['000333.XSHE', '600498.XSHG', '600616.XSHG']
	# event df
	event_df = pd.DataFrame(index=index, columns=columns)

	# loop over rows of df
	for date, row in df.iterrows():
		code = complete_code(str(row['股票代码']))
		# code has meaning and title pass the filter
		if code and filter_title(row['公告标题']):
			try:
				# keep only year-month-day, convert to datetime, index is list of trading dates 
				event_df.loc[adjust_to_trading_date(date, index), code] = 1
			except:
				print('Set event error at :{}, code :{}'.format(date, code))

	print(event_df)
	return event_df


announce2event('small.csv')