from lxml import html
import json
import requests
import time
import datetime 
import copy
from bs4 import BeautifulSoup
import re

from credentials import *
import traceback
'''
 dfb = a_link.xpath('./following-sibling::*[count(.| ./following-sibling::a[1]/preceding-sibling::*)=count(./following-sibling::a[1]/preceding-sibling::*)]')
'''

# INPUT_FILE = f'{HTML_OUTPUT}.html'
OUTPUT_FILE = 'send_json.json'


def get_original_url(url_):
	''' Helps to regenerate the url
	'''
	url = url_
	try:
		# print('url: {}'.format(url_))
		success = False
		for x in range(0, 3):
			try:
				r = requests.get(url_, timeout=10)
				success = True
				break
			except Exception:
				time.sleep(3)
				print(traceback.format_exc())
		if success:
			url = r.url
			techcrunch = True if 'techcrunch.com' in url else False
			if techcrunch:
				c = 0
				while c <= 3:
					c += 1
					print('get techcrunch, {} attempt'.format(c))
					try:
						soup = BeautifulSoup(r.text, 'lxml')
						url = soup.find('div', class_='article-content').find('a')['href']
						print('new url from techcrunch: {}'.format(url))
						break
					except:
						time.sleep(3)
						r = requests.get(url_)
						continue
			else:
				print('new url: {}'.format(url))
		else:
			print('cannot fetch url: {}'.format(url))
	except Exception:
		print(traceback.format_exc())
	return url
	

def duplicate_checker(demo_dict, check_dict):
	''' Helps to remove the duplicates in json file
	'''
	for d_ in demo_dict:
		if d_['name'] == check_dict['name']:
			return False
	return True





def save_dict(list_file):
	''' Saves the json file in dictionary
	'''
	with open(OUTPUT_FILE,'w') as out_file:
		json.dump(list_file,out_file, indent=2, ensure_ascii=False)
	return OUTPUT_FILE


def parse_html(INPUT_FILE):
	'''
	-- OPENS THE HTML
	-- PARSES THE HTML
	-- SAVES THE HTML
	'''
	print('parse {}'.format(INPUT_FILE))
	blacklist = []
	with open(INPUT_FILE,'r', encoding='UTF-8') as html_file:
		list_of_text = []

		# soup = BeautifulSoup(html_file.read())

		page = html.fromstring(html_file.read())
		print(page)
		list_of_deals = page.xpath('//span[contains(@style,"16px")]')
		print('list_of_deals: {} (count: {})'.format(list_of_deals, len(list_of_deals)))
		list_of_links = page.xpath('//p[contains(@style,"16px")]//a')
		# list_of_deals = list(set(list_of_deals))
		# for l in list_of_deals:
			# print(l.xpath('./text()'))
		# It will create an list of details
		full_text = ' '.join(df.xpath('string()') for df in page.xpath('//p[contains(@style,"16px")]'))
		list_of_details = {}
		for l in list_of_deals:
			if l.xpath('./text()') != []:
				list_of_details[l.xpath('./text()')[0]] = []
		list_of_deals_text = []
		for l in list_of_deals:
			if l.xpath('./text()') != []:
				list_of_deals_text.append(l.xpath('./text()')[0])
		for deals in list_of_deals:
			a_links = deals.xpath('./following-sibling::a')
			for a_link in a_links:
				try:
					key_name =  a_link.xpath('./preceding-sibling::strong[contains(@style,"19px")][1]')[0].xpath('./text()')[0]
					# print('key_name: {}'.format(key_name))
				except:
					pass
				try:
					if key_name:
						
						details = {}
						link_ = a_link.xpath('./@href')[0]
				
						name_ = a_link.xpath('.//text()')[0]
						details['name'] = name_
						if details['name'] not in blacklist:
							details['link'] = get_original_url(link_ )
							details['updated_date'] = datetime.datetime.today().strftime('%Y-%m-%d')
							details['email_date'] = INPUT_FILE.split('/')[-1].replace('.html', '')
					   		
						# # # strange stuff from prev dev
						# if duplicate_checker(list_of_details[key_name], details):
						# 	details['link'] = get_original_url(link_)
						
							list_of_details[key_name].append(details)
							save_dict(list_of_details)
							blacklist.append(details['name'])
						else:
							print('{} is already in json'.format(details['name']))


				except Exception:
					print('no key_name')
					print(traceback.format_exc())
					continue


		return list_of_details,full_text,list_of_deals_text
def get_deals(venture_dict, full_text, next_key):
	'''
	Returns the venture deals
	'''
	list_of_names = [df['name'] for df in venture_dict]
	# print('list_of_names: {}'.format(venture_dict))
	list_of_new = []
	for i,item_ in enumerate(venture_dict):
		details = copy.deepcopy(item_)
		item = item_['name']
		try:
			text_file = full_text[full_text.index(item):full_text.index(list_of_names[i+1])]
		except IndexError:
			text_file = full_text[full_text.index(item):full_text.index(next_key)]
		if not text_file:
			text_file = full_text[full_text.index(item):]
		try:
			if '-based' in text_file:
				l = '-based'
			elif '-founded' in text_file:
				l = '-founded'
			else:
				l = None
				location = ''
			if l:
				get_location = text_file.split(l)[0]
				location = get_location.split(', ')[1]
				location = location.replace('a ', '').replace('an ', ' ')
				location = location.strip()
				print(location)
		except:
			location = ''

		try:
			amount = re.findall('[-+]?\d*\.\d+\s\w+|\d+\s\w+', text_file)[0]
		except:
			amount = ''
		try:
			if '-based' in text_file:
				description = text_file.split('-based')[1].split(',')[0].split('. ')[0]
			elif '-founded' in text_file:
				description = text_file.split('-founded')[1].split(',')[0].split('. ')[0]
			else:
				description = ''
		except:
			description = ''
		try:
			investors = re.findall('(?i)investors including([^.]+)', text_file) + re.findall('(?i)investors include([^.]+)', text_file)
			investors = investors[0].split(', ')
			print('investors: {}'.format(investors))
		except:
			investors = ''

		try:
			details['series'] = re.findall('in (.*) funding', text_file)[0].replace('in ', '').replace(' funding', '')
		except:
			details['series'] = ''

		details['location'] = location
		details['amount'] = amount
		details['description'] = description.strip()
		for i in range(11):
			investor = 'investor{}'.format(i)
			try:
				# print(investors[i])
				details[investor] = investors[i].strip()
			except:
				details[investor] = ''
		details['full_text'] = text_file
		list_of_new.append(details)
	# print('list_of_new: {}'.format(list_of_new))
	return list_of_new

def extract_venture_deals(venture_dict):
	pass

def get_private_equity(venture_dict, full_text, next_key):


	list_of_names = [df['name'] for df in venture_dict]
	list_of_new = []
	for i,item_ in enumerate(venture_dict):
		details = copy.deepcopy(item_)
		item = item_['name']
		try:
			text_file = full_text[full_text.index(item):full_text.index(list_of_names[i+1])]
		except IndexError:
			text_file = full_text[full_text.index(item):full_text.index(next_key)]
		if not text_file:
			text_file = full_text[full_text.index(item):]
		try:
			starting_text = full_text[full_text[:full_text.index(item)].rindex('-'):full_text.index(item)]
		except:
			starting_text = ''
		try:
			if '-based' in text_file:
				l = '-based'
			elif '-founded' in text_file:
				l = '-founded'
			else:
				l = None
				location = ''
			if l:
				get_location = text_file.split(l)[0]
				location = get_location.split(', ')[1]
				location = location.replace('a ', '').replace('an ', ' ')
				location = location.strip()
				print(location)
		except:
			location = ''

		try:
			amount = re.findall('[-+]?\d*\.\d+\s\w+|\d+\s\w+', text_file)[0]
		except:
			amount = ''
		try:
			if '-based' in text_file:
				description = text_file.split('-based')[1].split(',')[0].split('. ')[0]
			elif '-founded' in text_file:
				description = text_file.split('-founded')[1].split(',')[0].split('. ')[0]
			else:
				description = ''
		except:
			description = ''
		try:
			investors = re.findall('(?i)investors including([^.]+)', text_file) + re.findall('(?i)investors include([^.]+)', text_file)
			investors = investors[0].split(', ')
			print('investors: {}'.format(investors))
		except:
			investors = ''

		try:
			details['series'] = re.findall('in (.*) funding', text_file)[0].replace('in ', '').replace(' funding', '')
		except:
			details['series'] = ''

		details['location'] = location
		details['amount'] = amount
		details['description'] = description.strip()
		for i in range(11):
			investor = 'investor{}'.format(i)
			try:
				# print(investors[i])
				details[investor] = investors[i].strip()
			except:
				details[investor] = ''
		details['full_text'] = starting_text + text_file
		list_of_new.append(details)
	return list_of_new
def main(INPUT_FILE):
	starting_link = ['VENTURE DEALS', 'IPO', 'SPAC', 'F+FS', 'PEOPLE']
	return_file,full_text,list_of_deals_text = parse_html(INPUT_FILE)
	new_list = {}
	for rf in return_file:
		print('rf: {}'.format(rf))
		kt = {}
		index_number = list_of_deals_text.index(rf)
		try:
			next_key_name = list_of_deals_text[index_number+1]
		except:
			next_key_name = rf

		# if starts with a link
		if rf in starting_link:
			print('get deals')
			venture_deals = get_deals(return_file[rf],full_text, next_key_name)
		else:
			print('get private eq')
			venture_deals = get_private_equity(return_file[rf],full_text, next_key_name)
		new_list[rf] = venture_deals
	### strange stuff from previous developer
	# if new_list.get('VENTURE DEALS'):
	#     print('venture deals in new_list')
	#     new_list['VENTURE DEALS'] = extract_venture_deals(new_list['VENTURE DEALS'])
	output_json = save_dict(new_list)

   #return list_of_text
