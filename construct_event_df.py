# -*- coding:utf-8 -*-
from util_quant import *

def filter_title(title):
	# word must be in title
	contain = False
	if '增持' in title:
		contain = True
		if '完成' in title:	# if contain both words, must be right
			return True

	# words that should not be in title
	exclude_list = ['误操作', '倡议书', '进展', '核查意见', '补充', '计划' ]
	for w in exclude_list:
		if w in title:
			return False

	return contain

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
	# get all valid trading dates
	trading_dates = get_trading_dates(start_date, end_date)
	# event df
	event_df = pd.DataFrame()

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

if __name__ = '__main__':
	announce2event('small.csv')
