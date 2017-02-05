import requests
import urllib.parse
from bs4 import BeautifulSoup
import re
import argparse

input_type = 0
output_type = 0
ccd = None
ck = None
results = []
fmt_str = '%w：%m'

parser = argparse.ArgumentParser(description='Chinese-Chinese Dictionary Crawler')
parser.add_argument('keywords', nargs=argparse.REMAINDER)
parser.add_argument('-s', '--strformat', type=str)
parser.add_argument('-f', '--file', type=str)
parser.add_argument('-o', '--output', type=str)
args = vars(parser.parse_args())
if args['strformat'] != None:
	fmt_str = args['strformat']
if args['file'] != None:
	input_type = 1
if args['output'] != None:
	output_type = 1

def renew_session():
	global ccd, ck
	res = requests.get('http://dict.revised.moe.edu.tw/cgi-bin/cbdic/gsweb.cgi/?&o=dcbdic')
	ck = res.cookies['new_www_edu_Tw']
	soup = BeautifulSoup(res.text, 'html.parser')
	a = soup.find('a')['href']
	ccd = a[a.find('ccd')+4:].split('&')[0]

def parse_soup(soup):
	fields = soup.find_all('th', class_='std1')
	ret = dict()
	for field in fields:
		if field.b.string.find('字詞') != -1:
			ret['word'] = field.next_sibling.get_text().strip('【】')
		elif field.b.string.find('注音') != -1:
			ret['bopomofo'] = field.next_sibling.get_text()
		elif field.b.string.find('拼音') != -1:
			ret['pinyin'] = field.next_sibling.get_text()
		elif field.b.string.find('釋義') != -1:
			ret['meaning'] = field.next_sibling.get_text()
	return ret

def parse_page(url):
	global ccd, ck
	res = requests.get(url, cookies={'new_www_edu_Tw': ck})
	soup = BeautifulSoup(res.text, 'html.parser')
	return parse_soup(soup)

def get_resultstr(result):
	tmp = fmt_str;
	return tmp.replace('%w', result['word']) \
		.replace('%b', result['bopomofo']) \
		.replace('%p', result['pinyin']) \
		.replace('%m', result['meaning'])

def print_results():
	if output_type == 0:
		for result in results:
			print(get_resultstr(result))
	elif output_type == 1:
		fout = open(args['output'], 'w')
		for result in results:
			fout.write(get_resultstr(result) + '\n')
		fout.close()

def lookup(word):
	payload = {'o': 'e0', 'ccd': ccd, 'sec': 'sec1', 'qs0': word, 'clscan': '', 'selectmode': 'mode1', 'button.x': '0', 'button.y': '0', 'button': '提交'}
	res = requests.post('http://dict.revised.moe.edu.tw/cgi-bin/cbdic/gsweb.cgi', data=payload, cookies={'new_www_edu_Tw': ck})
	soup = BeautifulSoup(res.text, 'html.parser')
	tmp = soup.find('div', class_='menufmt1')
	if (tmp == None):
		num = 1
	else:
		num = int(tmp.find('font', class_='numfont').string)
	
	res = dict()
	if (num == 0):
		res = {'word': word, 'bopomofo': '', 'pinyin': '', 'meaning': ''}
	elif (num == 1):
		res = parse_soup(soup)
	else:
		''' find links the proper way - probably better if new modes are added
		maintds = soup.find_all('td', class_=re.compile('maintd'))
		for td in maintds:
			if td.a != None:
				print(td.a['href'])
		'''
		res = parse_page('http://dict.revised.moe.edu.tw/cgi-bin/cbdic/gsweb.cgi?ccd=%s&o=e0&sec=sec1&op=v&view=0-1' %(ccd))
	results.append(res)

renew_session()

if input_type == 0: # Parse input from command line arguments
	for keyword in args['keywords']:
		lookup(keyword)
elif input_type == 1: # Parse input from file
	try:
		fin = open(args['file'])
	except:
		print('Error: Specified input file doesn\'t exist')
	else:
		line = fin.readline()
		keywords = line.split(' ')
		for keyword in keywords:
			lookup(keyword.strip())
		fin.close()

print_results()

