# -*- coding:utf-8 -*-

import urllib
import urllib2
import re
import os
import time
import datetime

import json
import csv


IGNORED_FILE_TYPE = dict()	# dict of ignored file types

def json_to_df(resp_json, column, csv_file):

	for item in resp_json['announcements']:
		info_list = list()
		try:
			info_list.append(str(item['secCode']).encode('utf-8'))	# code
			info_list.append(item['announcementTitle'].encode('utf-8'))	# title
		except:
			print('the stock that can not be append to info_list has code: '.format(item['secCode']))
			print('the stock that can not be append to info_list has title: '.format(item['announcementTitle']))
			continue

		# save downloadable url for announcement document
		doc_type = item['adjunctType']
		url = str()
		# construct url for each file type
		if doc_type == 'DOCX' or doc_type == 'DOC':
			base_url = 'http://www.cninfo.com.cn/cninfo-new/disclosure/{}/bulletin_detail/false/{}?announceTime={}'
			url_info = item['adjunctUrl'].split('/')
			# get rid of file type of ID
			announce_id = url_info[2].split('.')[0]
			url = base_url.format(column, announce_id, url_info[1])
		elif doc_type == 'PDF':
			base_url = 'http://www.cninfo.com.cn/cninfo-new/disclosure/{}/download/{}?announceTime={}'
			url_info = item['adjunctUrl'].split('/')
			# get rid of file type of ID
			announce_id = url_info[2].split('.')[0]
			url = base_url.format(column, announce_id, url_info[1])
		else:	# record ignored file types
			if doc_type not in IGNORED_FILE_TYPE:
				IGNORED_FILE_TYPE[doc_type] = 0
			else:
				IGNORED_FILE_TYPE[doc_type] += 1
		info_list.append(url.encode('utf-8'))	# file url

		timestamp = item['announcementTime']
		timestamp //= 1000	# get rid of last 3 digits
		info_list.append(datetime.datetime.fromtimestamp(timestamp))	# date
		# skip ones that has doc tpye other than DOC DOCX and PDF
		if doc_type not in ['DOCX', 'DOC', 'PDF']:
			continue
		# write info_list into csv file
		with open(csv_file, 'a') as csv_w:
			writer = csv.writer(csv_w, quoting=csv.QUOTE_ALL)
			writer.writerow(info_list)


# crawl one day
def cninfo_http_post(start_date):
	print('Crawling announcements at {}'.format(start_date))
	response_list = list()
	pn = 1
	page_size = 30
	url = 'http://www.cninfo.com.cn/cninfo-new/announcement/query'
	while pn:
		values = {'column':column, 'pageNum':pn, 'pageSize':page_size, 'seDate':start_date}	# header?
		jdata = urllib.urlencode(values)
		# time.sleep(0.1)
		request = urllib2.Request(url, jdata, values)
		while True:
			try:
				response = urllib2.urlopen(request)
			except:
				time.sleep(1)
				continue
			break
		resp = response.read()
		has_more = re.findall(r'.*?\"hasMore\":tru(.*?)}', resp)
		response_list.append(resp)
		pn = pn + 1
		# print jdata
		# print '-------------->>>page: '+str(pn-1)+'<<<-----------------'
		if not has_more:
			break
	return response_list

# crawl days of info start from start_date
def cninfo_to_df(days, start_date, column):

	csv_file = 'all.csv'
	# # create a csv file to save all announcements
	# with open(csv_file, 'wb') as csv_w:
	#	wr = csv.writer(csv_w, quoting=csv.QUOTE_ALL)
	#	wr.writerow(['股票代码', '公告标题', '公告链接', '日期'])

	date_time = time.mktime(time.strptime(start_date, '%Y-%m-%d'))
	while days > 0:
		response_list = cninfo_http_post(start_date)
		# save into plain files
		str_list = "".join(response_list)
		li = open('./file/' + start_date + '_' + column, 'w+')
		li.write(str_list)
		li.close()
		# save into csv file
		for response in response_list:
			response_json = json.loads(response)
			json_to_df(response_json, column, csv_file)	# write into csv file
		# update date
		date_time = date_time - 86400 # 86400sec = 24hr
		time_stamp = time.localtime(date_time)
		start_date = time.strftime('%Y-%m-%d', time_stamp)
		# print '------------------next date is ' + start_date + '-----------------------'
		days = days - 1

if __name__ == '__main__':

	start_date = '2012-11-01' # start date
	days = 2000	# days to crawl
	column = 'sse'	# sse:沪市公告, szse:深市公告, hke:香港公告, not working, just ignore this
	cninfo_to_df(days, start_date, column)
	print('Ignored file types')
	print(IGNORED_FILE_TYPE)

# {u'PPTX': 17, u'TXT': 24943, u'XLS': 3, u'PPT': 8}
# {u'PPTX': 4, u'TXT': 24538, u'XLS': 1, u'PPT': 2}
