from util_quant import *
from signal_quant import *

HEAD_EXPAND_NUM = 20
TAIL_EXPAND_NUM = 20
## Event class
class Event:
    """Back test performance based on rate of return chosen by a specific event
    
    :param event_df: DataFrame of events, stock on column, date on row
    """

    def __init__(self, event_df):
        print("Generating event instance...")
        # initialize vars
        self.event_df = event_df # date in row, stock index in column
        self.event_list = list()
        self.price_df = event_df * np.nan
        self.absolute_performance = pd.DataFrame()
        self.relative_performance = pd.DataFrame()
        # get data
        self.get_prices()
        self.get_event_list()
        print("")
    
    # construct list of events from event_df        
    def get_event_list(self):
        # build a list of tuples (s_index, e_date)
        print("Generating event_list...")
        # loop over rows of event_df
        for event_date, row in self.event_df.iterrows():
            # NOTICE: event_df has elements of type 'Object', which are pointers to objects, has to get object itself first
            row_drop = row[np.isfinite(row.values.astype(np.float64))] # drop all NaN, left only events
            # loop over every element in row series
            for stock_index, event_indicator in row_drop.iteritems(): # event_indicator is always 1
                self.event_list.append((stock_index, event_date))
        print('Done! Found totally {} events.'.format(len(self.event_list)))
        
    def get_prices(self, fields='close', adjust_type='post', frequency='1d'):
        # collect prices needed
        print("Collecting price data...")
        # self.events.df.columns contains stock codes
        stock_list = list(self.event_df.columns)
        # self.events.df.index contains dates we need
        s_date = self.event_df.index[0] - HEAD_EXPAND_NUM*BDay()
        e_date = self.event_df.index[-1] + TAIL_EXPAND_NUM*BDay()
        
        self.price_df = get_price(stock_list,
                                  start_date=s_date,
                                  end_date=e_date,
                                  fields=fields,
                                  adjust_type=adjust_type,
                                  frequency=frequency)
        

        
    def get_absolute_performance(self, lookforward_num, lookbackward_num=0, boll_std_num=1):
        """Compute and plot absolute rate of return
        
        :param lookforward_num: Number of days in concern in the future
        :param lookforward_num: Number of days in concern in the past, if not specified, ignore
        """
        print("Calculating absolute performance")
        # rows are events, columns are days
        absolute_performance_list_forward = list()
        absolute_performance_list_backward = list()
        
        # iterate to analyze every event in self.events_list
        for e in self.event_list:
            # event data format: tuple(code_of_event_stock, date_of_the_event)
            stock = e[0]
            date = e[1]
            # get location number of current date
            event_row = self.price_df.index.get_loc(date)
            forward_row = min(event_row + lookforward_num, len(self.price_df))
            if lookbackward_num > 0: 
                backward_row = max(event_row - lookbackward_num, 0)

            try: # deal with lookforward
                # slice prices during target period
                price_forward = self.price_df.ix[event_row:(forward_row+1), stock]
                # transform price to net value, nv = 1 + accumulated return rate, then minus 1
                net_value_forward = (price_forward / price_forward[0]).values - 1
                # append nv for this event to the total performance list
                absolute_performance_list_forward.append(net_value_forward)
            except:
                # print relavent variables for debugging purpose
                print('slice price error at event row: {}'.format(event_row))
                print('slice price error at forward row: {}'.format(forward_row))
            
            if lookbackward_num > 0: # deal with lookbackward
                try:  
                    price_backward = self.price_df.ix[backward_row:(event_row+1), stock]
                    # reverse the order to align event_row, [event_day, event_day-1, ...]
                    price_backward = price_backward.sort_index(ascending=False)
                    # transform price to net value, nv = 0 + accumulated returns
                    net_value_backward = (price_backward / price_backward[0]).values - 1
                    absolute_performance_list_backward.append(net_value_backward)
                except:
                    print('slice price error at event row: {}'.format(event_row))
                    print('slice price error at backward row: {}'.format(backward_row))
        
        # transform list of arrays to DataFrame
        absolute_performance_df_forward = pd.DataFrame(absolute_performance_list_forward)
        
        if lookbackward_num > 0:
            # create and then reverse order of backward dataframe [event_day-n, event_day-n-1, ..., event_day]
            absolute_performance_df_backward = pd.DataFrame(absolute_performance_list_backward)
            absolute_performance_df_backward = absolute_performance_df_backward.sort_index(axis=1, ascending=False)
            # rename columns to negative day representation
            columns_backward = range(1-absolute_performance_df_backward.shape[1], 1)
            absolute_performance_df_backward.columns = columns_backward
            # concat forward and backward dataframe, drop one of repeated column 0, which is event day
            self.absolute_performance = pd.concat([absolute_performance_df_backward.drop(0, axis=1), 
                                                   absolute_performance_df_forward], axis=1)
        else:
            self.absolute_performance = absolute_performance_df_forward
        
        ## Plot    
        # plot average absolute performance
        plt.figure(figsize=(10, 6))
        absolute_performance_mean = self.absolute_performance.mean()
        graph = absolute_performance_mean.plot(kind='line')
        graph.set_title('Average Absolute Performance', fontsize=16)
        graph.set_xlabel('Day', fontsize=16)
        # force x axe show integer tick
        plt.xticks(absolute_performance_mean.index)
        graph.set_ylabel('Rate of return', fontsize=16)
        # plot Bollinger Band, default 1 std
        performance_mean_std = absolute_performance_mean.std()
        boll_up = absolute_performance_mean + boll_std_num * performance_mean_std
        boll_down = absolute_performance_mean - boll_std_num * performance_mean_std
        graph.fill_between(absolute_performance_mean.index, boll_down, boll_up, alpha=0.2)
        # plot horizontal line of 0 in red
        xmin, xmax = graph.get_xlim()
        graph.hlines(y=[0], xmin=xmin, xmax=xmax, color='r')
        plt.show()
        
        # plot win rate
        plt.figure(figsize=(10, 6))
        win_rate = self.absolute_performance.copy( )
        # mark value bigger than 0 as 1, others 0
        win_rate[win_rate > 0] = 1
        win_rate[win_rate <= 0] = 0
        # winning count divide by total number of events with respect to specific days
        day_count = win_rate.shape[0]
        win_rate = win_rate.sum(axis=0) / day_count
        graph2 = win_rate.plot(kind='line')
        graph2.set_title('Win Rate', fontsize=16)
        graph2.set_xlabel('Day', fontsize=16)
        # force x axe show integer tick
        plt.xticks(absolute_performance_mean.index)
        graph2.set_ylabel('Win rate', fontsize=16)
        plt.show()
        
        
    def get_relative_performance(self, benchmark_index, lookforward_num, lookbackward_num=0, boll_std_num=1):
        """Compute and plot relative rate of return, long-short portfolio
        
        :param benchmark_index: Benchmark to compare with
        :param lookforward_num: Number of days in concern in the future
        :param lookforward_num: Number of days in concern in the past, if not specified, ignore
        """
        print("Calculating relative performance")
        # collect benchmark index prices
        s_date = self.event_df.index[0] - HEAD_EXPAND_NUM*BDay()
        e_date = self.event_df.index[-1] + TAIL_EXPAND_NUM*BDay()
        fld = 'close'
        adj = 'post'
        frq= '1d'
        benchmark_price = get_price(benchmark_index,
                                    start_date=s_date,
                                    end_date=e_date,
                                    fields=fld,
                                    adjust_type=adj,
                                    frequency=frq)
        
        relative_performance_list_forward = list()
        relative_performance_list_backward = list()

        for e in self.event_list:
            stock = e[0]
            date = e[1]
            # get location number of current date
            event_row = self.price_df.index.get_loc(date)
            forward_row = min(event_row + lookforward_num, len(self.price_df))
            if lookbackward_num > 0:
                backward_row = max(event_row - lookbackward_num, 0)

            try: # deal with forward
                # slice prices during target period
                price_forward = self.price_df.ix[event_row:forward_row, stock]
                price_bench_forward = benchmark_price.ix[event_row:forward_row]
                # transform price to net value, nv = 1 + accumulated returns
                net_value_forward = (price_forward / price_forward[0]).values
                net_value_bench_forward = (price_bench_forward / price_bench_forward[0]).values
                # calculate and append relative performance for this event to the total performance list
                # NOTICE:
                # Unlike net value, relative_performance = 0 + accumulated long-short portfolio returns,
                # since both nv and nv_benchmark contains 1 and their cumrets(accumulated returns).
                relative_performance_forward = net_value_forward - net_value_bench_forward
                relative_performance_list_forward.append(relative_performance_forward)
            except:
                # print relavent variables for debugging purpose
                print('slice price error at event row: {}'.format(event_row))
                print('slice price error at forward row: {}'.format(forward_row))
            
            if lookbackward_num > 0: # deal with backward
                try:
                    # slice prices during target period
                    price_backward = self.price_df.ix[backward_row:(event_row+1), stock]
                    price_bench_backward = benchmark_price.ix[backward_row:(event_row+1)]
                    # reverse the order to aline event_row, [event_day, event_day-1, ...]
                    price_backward = price_backward.sort_index(ascending=False)
                    price_bench_backward = price_bench_backward.sort_index(ascending=False)
                    # transform price to net value, nv = 1 + accumulated returns
                    net_value_backward = (price_backward / price_backward[0]).values
                    net_value_bench_backward = (price_bench_backward / price_bench_backward[0]).values
                    # calculate and append relative performance for this event to the total performance list
                    # NOTICE:
                    # Unlike net value, relative_performance = 0 + accumulated long-short portfolio returns,
                    # since both nv and nv_benchmark contains 1 and their cumrets(accumulated returns).
                    relative_performance_backward = net_value_backward - net_value_bench_backward
                    relative_performance_list_backward.append(relative_performance_backward)
                except:
                    # print relavent variables for debugging purpose
                    print('slice price error at event row: {}'.format(event_row))
                    print('slice price error at backward row: {}'.format(backward_row))

        # transform list of arrays to DataFrame        
        relative_performance_df_forward = pd.DataFrame(relative_performance_list_forward)

        if lookbackward_num > 0:
            # create and then reverse order of backward dataframe [event_day-n, event_day-n-1, ..., event_day]
            relative_performance_df_backward = pd.DataFrame(relative_performance_list_backward)
            relative_performance_df_backward = relative_performance_df_backward.sort_index(axis=1, ascending=False)
            # rename columns to negative day representation
            columns_backward = range(1-relative_performance_df_backward.shape[1], 1)
            relative_performance_df_backward.columns = columns_backward
            # concat forward and backward dataframe, drop one of repeated column 0, which is event day
            self.relative_performance = pd.concat([relative_performance_df_backward.drop(0, axis=1), 
                                                   relative_performance_df_forward], axis=1)
        else:
            self.relative_performance = relative_performance_df_forward
        
        ## Plot
        # plot average relative performance
        plt.figure(figsize=(10, 6))
        relative_performance_mean = self.relative_performance.mean()
        graph = relative_performance_mean.plot(kind='line')
        graph.set_title('Average Relative Performance', fontsize=16)
        graph.set_xlabel('Day', fontsize=16)
        # force x axe show integer tick
        plt.xticks(relative_performance_mean.index)
        graph.set_ylabel('Rate of return', fontsize=16)
        # plot Bollinger Band, default 1 std
        performance_mean_std = relative_performance_mean.std()
        boll_up = relative_performance_mean + boll_std_num * performance_mean_std
        boll_down = relative_performance_mean - boll_std_num * performance_mean_std
        graph.fill_between(relative_performance_mean.index, boll_down, boll_up, alpha=0.2)
        # plot horizontal line of 0 in red
        xmin, xmax = graph.get_xlim()
        graph.hlines(y=[0], xmin=xmin, xmax=xmax, color='r')
        plt.show()
        
        # plot win rate
        plt.figure(figsize=(10, 6))
        win_rate = self.relative_performance.copy( )
        # mark value bigger than 0 as 1, others 0
        win_rate[win_rate > 0] = 1
        win_rate[win_rate <= 0] = 0
        # winning count divide by total number of events with respect to specific days
        day_count = win_rate.shape[0]
        win_rate = win_rate.sum(axis=0) / day_count
        graph2 = win_rate.plot(kind='line')
        graph2.set_title('Win Rate', fontsize=16)
        graph2.set_xlabel('Day', fontsize=16)
        # force x axe show integer tick
        plt.xticks(relative_performance_mean.index)
        graph2.set_ylabel('Win rate', fontsize=16)
        plt.show()
    
    def event_distribution(self, month=True):
        # plot event distribution by month or by day, depend on parameter 'month'
        print('Plotting event distribution...')
        if month:   # count by month   
            # group index by month, then sum over month, need to convert index to datetime first!
            event_df_month = self.event_df.copy()
            event_df_month.index = pd.to_datetime(event_df_month.index)
            event_df_month = event_df_month.resample('M').sum()
            # sum over column
            event_count_month = event_df_month.sum(axis=1)
            # modify index, keep only year and month
            index_new = pd.Series(event_count_month.index)
            index_new = index_new.apply(date2ym_str)
            event_count_month.index = index_new
            # plot
            plt.figure(figsize=(10, 6))
            graph = event_count_month.plot(kind='bar')
            graph.set_title('Event Distribution', fontsize=16)
            graph.set_xlabel('Month', fontsize=16)
            graph.set_ylabel('Event count', fontsize=16)
            plt.show()

        else:   # count by day
            # sum over column
            event_count_day = self.event_df.sum(axis=1)
            # plot
            plt.figure(figsize=(10, 6))
            graph = event_count_day.plot(kind='bar')
            graph.set_title('Event Distribution', fontsize=16)
            graph.set_xlabel('Date', fontsize=16)
            graph.set_ylabel('Event count', fontsize=16)
            plt.show()

