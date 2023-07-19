from bs4 import BeautifulSoup
import requests
import lxml
import pandas as pd
from datetime import datetime
# 

band_name = input('Please, enter a band name:\n')
print()
print(f'Searching {band_name}. Wait, please...')
print()
base_url = 'https://www.etsy.com'
search_url = f'https://www.etsy.com/in-en/shop/{band_name}/sold/'
data = {
	'Date-Time': [],
	'Seller-Name': [],
	'Seller-Location': [],
	'URL': [],
	'Product-Name': [],
	'People-Cart-Details': [],
	'Total-Sales-As-Of': [],
	'total-reviews':[],
    }


def export_table_and_print(data):
	table = pd.DataFrame(data, columns=['Date-Time', 'Seller-Name', 'Seller-Location', 'URL','Product-Name', 'People-Cart-Details', 'Total-Sales-As-Of','total-reviews'])
	table.index = table.index+1
	# table.to_csv(f'{band_name}_albums.csv',sep=',', encoding='utf-8', index=False)
	print('scrapint done. Here is the result')
	print(table)

def get_sales_item_details(soup,brnd,location,link,number_sold,number_of_reviews):
	#loop for individual cards
	title = soup.select('h3')[0].get_text().strip()
	try:
		Cart_Details = (soup.find('div', class_='wt-text-brick wt-text-caption wt-pt-xs-1').text).strip()
	except:
		Cart_Details = None
	# # Store the values into the 'data' object
	data['Date-Time'].append(datetime.now())
	data['Seller-Name'].append(brnd)#
	data['Seller-Location'].append(location)#
	data['URL'].append(link)#
	data['Product-Name'].append(title)
	data['People-Cart-Details'].append(Cart_Details)
	data['Total-Sales-As-Of'].append(number_sold)#
	data['total-reviews'].append(number_of_reviews)#



def parse_page(next_url):
	headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'}
	#
	page = requests.get(next_url,headers=headers)
	# check
	if page.status_code == requests.codes.ok:
		bs = BeautifulSoup(page.content,'lxml')
		# fetch all
		total_sold = ((bs.find('div',class_='hide-xs text-gray-lightest text-smaller ml-xs-2').text).strip()).split(' ')
		# Favourite_shop = bs.find("span", {"data-region":"num-favorers"})
		number_of_reviews = ((bs.find('span',class_='vertical-align-top').text).strip())[1:4]
		brnd,location = list((i.text).strip() for i in  bs.findAll('div', class_='hide-xs hide-sm'))
		list_all_cards = bs.findAll('div',class_='js-merch-stash-check-listing')
		for item in bs.select('.wt-grid__item-md-4'):
			get_sales_item_details(item,brnd,location,next_url,total_sold[0],number_of_reviews)
		###
		try:	
			next_page_text = bs.find('ul', class_='btn-group-md list-unstyled text-left').findAll('li')[-1]['class'][-1]
			if next_page_text == 'btn-group-item-md':
				next_page_partial = bs.find('ul', class_='btn-group-md list-unstyled text-left').findAll('li')[-1].find('a')['href']
				parse_page(next_page_partial)
			else:
				export_table_and_print(data)
		except:
			export_table_and_print(data)
		

	
parse_page(search_url)
