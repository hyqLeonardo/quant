from util_quant import *
from signal_quant import *

## Event class
class Event:
	"""Test rate of return of a specific event
	
	:param stock_list: A list of stock pool.
	:param signal_func: The function to fetch signals from stock series 
	:param period: The period of time concerned, e.g. 300 means 300 dyas before (today-5)
	"""

	def __init__(self, events_df):
		self.events_df = events_df
		self.event_list = list()
		self.get_event_list()

	# def __init__(self, stock_list, signal_func, period):
	# 	self.stock_list = stock_list
	# 	self.signal_func = signal_func
	# 	self.period = period
	# 	self.event_list = list()
	# 	self.fetch_event(stock_list, signal_func, period, self.event_list)
	# 	if len(self.event_list) == 0:	# exit if no event found
	# 		sys.exit('No event found !')
	
	# def fetch_event(self, stock_list, signal_func, period, event_list):
	# 	for stock_index in stock_list:
	# 		event_list.extend(signal_func(stock_index, period))

	def get_event_list(self):
		# build a list of tuples (s_index, e_date)
		for e_date, row in self.events_df.iterrows():
			row_drop = row[np.isfinite(row)] # drop all NaN, only left events
			for s_index, e in row_drop.iteritems():	# e is always 1
				self.event_list.append((s_index, e_date))

	def absolute_return(self, lookforward_num, lookback_num, plot=True):
		# lookforward_num and lookback_num must be bigger than 0
		if lookforward_num < 1 or lookback_num < 1:
			sys.exit('lookforward_num and lookforward_num can only take value bigger or equal to 1 !')

		# dataframe of prices of each event
		# (day)
		# 	 	  0    1  ...  n-1    n		(event)
		# 0	 
		# 1	
		# 2	 	(ele) represents the third day after
		# .		 event day
		# .
		# .
		# m
		e_count = 0 
		for s_index, e_date in self.event_list:
			# adjust encapsulate to a function called get_price_days
			price_aft = get_price(s_index, start_date=e_date, end_date=shift_date(e_date, lookforward_num), adjust_type='post', fields='close')
			price_pre = get_price(s_index, start_date=shift_date(e_date, -lookback_num), end_date=e_date, adjust_type='post', fields='close')
			price_aft = price_aft[:lookforward_num]
			price_pre = price_pre[-lookback_num:]
			# reindex with interger and pad with NaN
			price_aft = pad_series(price_aft, lookforward_num, aft=True)
			price_aft.name = e_count
			price_pre = pad_series(price_pre, lookback_num, aft=False)
			price_pre.name = e_count
			if e_count == 0:	# create df first
				price_aft_df = price_aft
				price_pre_df = price_pre
			else:	# concat for every event
				price_aft_df = pd.concat([price_aft_df, price_aft], axis=1)
				price_pre_df = pd.concat([price_pre_df, price_pre], axis=1)
			e_count += 1
		# accumulated return rate of each event
		rate_aft_df = price_aft_df.copy()
		rate_pre_df = price_pre_df.copy()
		for d in range(lookforward_num):
			rate_aft_df.loc[lookforward_num-1-d] = rate_aft_df.loc[lookforward_num-1-d]/rate_aft_df.loc[0]-1
		for d in range(1-lookback_num, 1):
			rate_pre_df.loc[d] = rate_pre_df.loc[d]/rate_pre_df.loc[0]-1
		# concat two dataframe, date in column, event in row
		rate_df = pd.concat([rate_pre_df.drop([0]).T, rate_aft_df.T], axis=1)
		# get the average rate
		rate_mean = rate_df.mean()	# average of rows
		# get series of max and min rate of each column
		rate_max = rate_df.max()
		rate_min = rate_df.min()

		if plot:
			graph = rate_mean.plot(kind='line')
			# plot horizontal line of 0 in red
			xmin, xmax = graph.get_xlim()
			graph.hlines(y=[0], xmin=xmin, xmax=xmax, color='r')		
			graph.fill_between(rate_min.index, rate_min, rate_max, alpha=0.5)

	def excess_return(self, lookforward_num, lookback_num, benchmark, plot=True):
		# lookforward_num and lookback_num must be bigger than 0
		if lookforward_num < 1 or lookback_num < 1:
			sys.exit('lookforward_num and lookforward_num can only take value bigger or equal to 1 !')
		# compute mainly use Series, combine in the end
		e_count = 0 
		for s_index, e_date in self.event_list:
			# get historical data of each event, while the dates of stock corresponds with index
			index_aft = get_price(benchmark, start_date=e_date, end_date=shift_date(e_date, lookforward_num), adjust_type='post', fields='close')
			stock_aft = get_price(s_index, start_date=e_date, end_date=shift_date(e_date, lookforward_num), adjust_type='post', fields='close')
			stock_aft = stock_aft.reindex(index_aft.index)	# reindex stock price based on index price
			index_aft = index_aft[:lookforward_num]
			stock_aft = stock_aft[:lookforward_num]
			index_pre = get_price(benchmark, start_date=shift_date(e_date, -lookback_num), end_date=e_date, adjust_type='post', fields='close')
			stock_pre = get_price(s_index, start_date=shift_date(e_date, -lookback_num), end_date=e_date, adjust_type='post', fields='close')
			stock_pre = stock_pre.reindex(index_pre.index)
			index_pre = index_pre[-lookback_num:]
			stock_pre = stock_pre[-lookback_num:]
			# reindex with interger and pad with NaN
			stock_aft = pad_series(stock_aft, lookforward_num, aft=True)
			index_aft = pad_series(index_aft, lookforward_num, aft=True)
			stock_aft.name = e_count
			index_aft.name = e_count
			stock_pre = pad_series(stock_pre, lookback_num, aft=False)
			index_pre = pad_series(index_pre, lookback_num, aft=False)
			stock_pre.name = e_count
			index_pre.name = e_count
			# comppute rate respectively, then extract bechmark from stock
			rate_index_aft = price_to_rate(index_aft, aft=True)
			rate_stock_aft = price_to_rate(stock_aft, aft=True)
			rate_index_pre = price_to_rate(index_pre, aft=False)
			rate_stock_pre = price_to_rate(stock_pre, aft=False)
			# cocat aft and pre, drop one of the base row (row 0)
			rate_index = pd.concat([rate_index_pre.drop([0]), rate_index_aft], axis=0)	
			rate_stock = pd.concat([rate_stock_pre.drop([0]), rate_stock_aft], axis=0)
			# excessive return 
			rate_excess = rate_stock - rate_index
			if e_count == 0:
				rate_excess_df = rate_excess
			else:	# concat every event's excess series to row of df
				rate_excess_df = pd.concat([rate_excess_df, rate_excess], axis=1)
			e_count += 1

		rate_excess_df = rate_excess_df.T # dates in column, events in row
		# get average excess rate
		rate_excess_mean = rate_excess_df.mean()
		# get series of max and min rate of each column
		rate_excess_max = rate_excess_df.max()
		rate_excess_min = rate_excess_df.min()

		if plot:
			graph = rate_excess_mean.plot(kind='line')
			# plot horizontal line of 0 in red
			xmin, xmax = graph.get_xlim()
			graph.hlines(y=[0], xmin=xmin, xmax=xmax, color='r')
			graph.fill_between(rate_excess_min.index, rate_excess_min, rate_excess_max, alpha=0.2)

	# show all results in one graph
	def show_result(self, lookforward_num, lookback_num, benchmark):
		self.absolute_return(lookforward_num, lookback_num)
		self.excess_return(lookforward_num, lookback_num, benchmark)
		blue_patch = mpatches.Patch(color='blue', label='Absolute Return')
		orange_patch = mpatches.Patch(color='orange', label='Excess Return')
		plt.legend(handles=[blue_patch, orange_patch])

