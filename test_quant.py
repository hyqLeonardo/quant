# test examples

# df = pd.DataFrame([[np.nan, 2, np.nan, 0], [3, 4, np.nan, 1], 
# 					[np.nan, np.nan, np.nan, 5]],
# 					columns=list('ABCD'))

# df.append(pd.DataFrame([[53]]))
# print(df)

# input examples
d1 = datetime.strptime('2017-5-12', "%Y-%m-%d")
d2 = datetime.strptime('2017-6-1', "%Y-%m-%d")
d3 = datetime.strptime('2017-3-1', '%Y-%m-%d')

dates = [d1, d2]
dates_n = [d3, d1, d2]
s1 = pd.Series([1, np.nan], index=dates)
s2 = pd.Series([np.nan, 1], index=dates)
s1.name = '000001.XSHE'
s2.name = '000005.XSHE'
s1_n = pd.Series([np.nan, 1, np.nan], index=dates_n)
s2_n = pd.Series([np.nan, np.nan, 1], index=dates_n)
s3_n = pd.Series([1, np.nan, 1], index=dates_n)
s1_n.name = '000001.XSHE'
s2_n.name = '000005.XSHE'
s3_n.name = '600900.XSHG'


input = pd.concat([s1, s2], axis=1)
input_n = pd.concat([s1_n, s2_n, s3_n], axis=1)
print(input)
print(input_n)