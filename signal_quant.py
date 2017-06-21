from util_quant import *

# A dumb signal for test
def signal_random(stock_index, period):
	today = datetime.now()
	today_adjust = shift_date(today, -5)	# end at 5 days bfore today
	start_date = shift_date(today_adjust, -period)
	stock_price = get_price(stock_index, start_date=start_date, end_date=today_adjust, adjust_type='pre', fields='close')
	# iterate over price series
	event_list = list()
	for date, price in stock_price.iteritems():
		if random.uniform(0, 1) > 0.95:
			event_list.append((stock_index, date))

	return event_list