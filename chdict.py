import requests
import urllib.parse
from bs4 import BeautifulSoup
import re

ccd = None
ck = None

def renew_session():
	global ccd, ck
	res = requests.get('http://dict.revised.moe.edu.tw/cgi-bin/cbdic/gsweb.cgi/?&o=dcbdic')
	ck = res.cookies['new_www_edu_Tw']
	soup = BeautifulSoup(res.text, 'html.parser')
	a = soup.find('a')['href']
	ccd = a[a.find('ccd')+4:].split('&')[0]

def parse_soup(soup):
	fields = soup.find_all('th', class_='std1')
	# print(len(fields))
	for field in fields:
		if field.b.string.find('釋義') != -1:
			return field.next_sibling.get_text()

def parse_page(url):
	global ccd, ck
	# print(url)
	res = requests.get(url, cookies={'new_www_edu_Tw': ck})
	# print(res.text)
	soup = BeautifulSoup(res.text, 'html.parser')
	return parse_soup(soup)

def lookup(word):
	payload = {'o': 'e0', 'ccd': ccd, 'sec': 'sec1', 'qs0': word, 'clscan': '', 'selectmode': 'mode1', 'button.x': '0', 'button.y': '0', 'button': '提交'}
	res = requests.post('http://dict.revised.moe.edu.tw/cgi-bin/cbdic/gsweb.cgi', data=payload, cookies={'new_www_edu_Tw': ck})
	# print(res.text)
	soup = BeautifulSoup(res.text, 'html.parser')
	tmp = soup.find('div', class_='menufmt1')
	if (tmp == None):
		num = 1
	else:
		num = int(tmp.find('font', class_='numfont').string)
	if (num == 0):
		ret = ''
	elif (num == 1):
		data = parse_soup(soup)
		print(data)
	else:
		''' find links the proper way - probably better if new modes are added
		maintds = soup.find_all('td', class_=re.compile('maintd'))
		for td in maintds:
			if td.a != None:
				print(td.a['href'])
		'''
		data = parse_page('http://dict.revised.moe.edu.tw/cgi-bin/cbdic/gsweb.cgi?ccd=%s&o=e0&sec=sec1&op=v&view=0-1' %(ccd))
		print(data)

renew_session()
# print(ccd)
lookup('哈哈')

