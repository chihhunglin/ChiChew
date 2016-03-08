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

parser = argparse.ArgumentParser(description='Chinese-Chinese Dictionary Crawler')
parser.add_argument('keywords', nargs=argparse.REMAINDER)
parser.add_argument('-f', '--file', type=str)
parser.add_argument('-o', '--output', type=str)
args = vars(parser.parse_args())
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
	for field in fields:
		if field.b.string.find('釋義') != -1:
			return field.next_sibling.get_text()

def parse_page(url):
	global ccd, ck
	res = requests.get(url, cookies={'new_www_edu_Tw': ck})
	soup = BeautifulSoup(res.text, 'html.parser')
	return parse_soup(soup)

def print_results():
	if output_type == 0:
		for pair in results:
			print('%s：%s' %(pair['word'], pair['data']))
	elif output_type == 1:
		fout = open(args['output'], 'w')
		for pair in results:
			fout.write('%s：%s\n' %(pair['word'], pair['data']))
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
	if (num == 0):
		data = '沒有資料'
	elif (num == 1):
		data = parse_soup(soup)
	else:
		''' find links the proper way - probably better if new modes are added
		maintds = soup.find_all('td', class_=re.compile('maintd'))
		for td in maintds:
			if td.a != None:
				print(td.a['href'])
		'''
		data = parse_page('http://dict.revised.moe.edu.tw/cgi-bin/cbdic/gsweb.cgi?ccd=%s&o=e0&sec=sec1&op=v&view=0-1' %(ccd))
	# print('%s：%s' %(word, data))
	results.append({'word': word, 'data': data})

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

