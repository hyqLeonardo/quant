# -*- coding:utf-8 -*-
from util_quant import *

def filter_title(title):
    # word must be in title
    contain = False
    if '增持' in title:
        contain = True
        if '完成' in title:    # if contain both words, must be right
            return True

    # words that should not be in title
    exclude_list = ['误操作', '倡议书', '进展', '核查意见', '补充', '计划' ]
    for w in exclude_list:
        if w in title:
            return False

    return contain

def announce2event(file_name, backtest_start_date=None, verbose=False):
    '''
        @param file_name is the csv file of announcements to read from
        @param date is the start date of backtest
    '''

    # read csv file into dataframe
    df = pd.read_csv(file_name, dtype=str,
                    parse_dates=True,
                    index_col='Date',
                    usecols=['Code', 'Title', 'Link', 'Date'],
                    na_values=['nan'])
    
#     index = df.index
#     print(index)
#     new_index = index
#     for d in index:
#         print(d)
#         new_index.append(''.join(datetime.datetime.strptime(' '.join(str(index).split()), '%Y-%m-%d %H:%M:%S')))
#     df = df.reindex(new_index)
    #################################### check ###################################
    if verbose:
        print(df[-20:])
        print(type(df.index[0]))
        print(df.index[0])
        #print(df.index[0] > date2datetime(datetime.date(2017, 6, 12)))
        print(df.columns)
        # check index type
        for i in df.index:
            if i == '':
                print("There are null in df index!!!")
            elif not isinstance(i, type(datetime.datetime(2017,1,1))):
                print("There are {} type in df.index!!!".format(type(i)))
            else:
                pass
    #################################### check ###################################
    
    if backtest_start_date != None:
        try:
            # slice rows with date after backtest start date
            df = df[df.index > date2datetime(backtest_start_date)-BDay()]
        except:
            print('Something wrong when slice date of event df')

    # get date range
    start_date = date2ymd_str(df.index[-1])
    end_date = date2ymd_str(df.index[0])
    # get all valid trading dates
    trading_dates = get_trading_dates(start_date, end_date)
    # event df, no need to construct index and columns name, it's constructed on the fly
    event_df = pd.DataFrame(index=trading_dates)

    # loop over rows of df
    for date, row in df.iterrows():
        code = complete_code(str(row['Code']))
        # code has meaning and title pass the filter
        if date and code and filter_title(row['Title']):
#             try:
                # keep only year-month-day, convert to datetime, index is list of trading dates 
                event_df.loc[adjust_to_trading_date(date, trading_dates), code] = 1
#             except:
#                 print('Set event error at :{}, code :{}'.format(date, code))
    
    # NOTICE: Remember to reverse the order of row because date index in 
    # csv file is in descending order, while date index in event_df should be
    # in ascending order.
    # event_df = event_df.iloc[::-1]

    return event_df

if __name__ == '__main__':
	announce2event('small.csv')
