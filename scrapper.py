from bs4 import BeautifulSoup
import requests
import lxml
import pandas as pd
from datetime import datetime
import os
# 

band_name = input('Please, enter a band name:\n')
print()
print(f'Searching {band_name}. Wait, please...')
print()
base_url = 'https://www.etsy.com'
search_url = f'https://www.etsy.com/in-en/shop/{band_name}/sold'
headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'}
data = {
	'Date-Time': [],
	'Seller-Name': [],
	'Seller-Location': [],
	'URL': [],
	'Product-Name': [],
	'price': [],
	'varients': [],
	'size': [],
	'People-Cart-Details': [],
	'Total-Sales-As-Of': [],
	'total-reviews': [],
    }

# saving the data in data Dictionarie to a csv file 
def export_table_and_print(data,pat):
	table = pd.DataFrame(data, columns=['Date-Time', 'Seller-Name', 'Seller-Location', 'URL','Product-Name', 'price', 'varients', 'size', 'People-Cart-Details', 'Total-Sales-As-Of','total-reviews'])
	table.index = table.index+1
	(table.iloc[::-1]).to_csv(pat,sep=',', encoding='utf-8', index=False)
	print('scrapint done.')
	# print(table)


# entering scraped data to data Dictionarie
def get_sales_item_details(soup,bs2,brnd,location,link,number_sold,number_of_reviews):

    # scrapping the common data which dose not very for individual items 
	title = soup.select('h3')[0].get_text().strip()
	# cart details
	try:
		Cart_Details = (soup.find('div', class_='wt-text-brick wt-text-caption wt-pt-xs-1').text).strip()
	except:
		Cart_Details = None

    # price
	try:
		cost = (bs2.find('p',class_='wt-text-title-03 wt-mr-xs-2').text).strip()
	except:
		cost = 'Sorry, this item is sold out'
	
	# varients
	try:
		drop_list = ','.join([ (x.text).strip() for x in (bs2.find('div',class_='wt-select 0-selector-container')).findAll('option')][1:])
	except:
		drop_list = None

	# size
	try:
		sze = ','.join([(x.text).strip() for x in (bs2.find('div',class_='wt-select 1-selector-container')).findAll('option')][1:])
	except:
		sze = None
	
	# Store the values into the 'data' object
	data['Date-Time'].append(datetime.now())
	data['Seller-Name'].append(brnd)#
	data['Seller-Location'].append(location)#
	data['URL'].append(link)#
	data['Product-Name'].append(title)
	data['price'].append(cost)#
	data['varients'].append(drop_list)#
	data['size'].append(sze)#
	data['People-Cart-Details'].append(Cart_Details)
	data['Total-Sales-As-Of'].append(number_sold)#
	data['total-reviews'].append(number_of_reviews)#




# first time scrapping a brand
def parse_page_1st(next_url,pth):
	page = requests.get(next_url,headers=headers)
	# check
	if page.status_code == requests.codes.ok:
		bs = BeautifulSoup(page.content,'lxml')

		####scrapping data from table#####
		total_sold = ((bs.find('div',class_='hide-xs text-gray-lightest text-smaller ml-xs-2').text).strip()).split(' ')
		# Favourite_shop = bs.find("span", {"data-region":"num-favorers"})
		number_of_reviews = ((bs.find('span',class_='vertical-align-top').text).strip())[1:4]
		brnd,location = list((i.text).strip() for i in  bs.findAll('div', class_='hide-xs hide-sm'))
		# list_all_cards = bs.find('div',class_='js-merch-stash-check-listing')

        # loop for every item on sold page
		for item in bs.select('.wt-grid__item-md-4'):
			#### item page request#####
			pr_id= item['data-listing-id']
			url2 = f'https://www.etsy.com/in-en/listing/{pr_id}'
			page2 = requests.get(url2,headers=headers)
			if page2.status_code == requests.codes.ok:
				bs2 = BeautifulSoup(page2.content,'lxml')
				# final entry
				get_sales_item_details(item,bs2,brnd,location,next_url, total_sold[0], number_of_reviews)
		# Page loop and saving first time  csv
		try:	
			next_page_text = bs.find('ul', class_='btn-group-md list-unstyled text-left').findAll('li')[-1]['class'][-1]
			if next_page_text == 'btn-group-item-md':
				next_page_partial = bs.find('ul', class_='btn-group-md list-unstyled text-left').findAll('li')[-1].find('a')['href']
				parse_page_1st(next_page_partial,pth)
			else:
				export_table_and_print(data,pth)
		except:
			export_table_and_print(data,pth)



# updating csv scrapping function
def parse_page_update(next_url,sol,dttt,pat):
	page3 = requests.get(next_url,headers=headers)
	# check
	if page3.status_code == requests.codes.ok:
		bs3 = BeautifulSoup(page3.content,'lxml')
		
		###Few data for table#####
		total_sold_cur = ((bs3.find('div',class_='hide-xs text-gray-lightest text-smaller ml-xs-2').text).strip()).split(' ')
		# Favourite_shop = bs.find("span", {"data-region":"num-favorers"})
		number_of_reviews_cur = ((bs3.find('span',class_='vertical-align-top').text).strip())[1:4]
		brnd_cur,location_cur = list((i.text).strip() for i in  bs3.findAll('div', class_='hide-xs hide-sm'))
		# list_all_cards = bs.find('div',class_='js-merch-stash-check-listing')
		
		# ## check diff  loop only runs if the diff in sold items if more the 1 and  diff in days of runnung script is more then 1##
		dff_sl =  int(total_sold_cur[0]) - int(sol)
		dff_tm = int(((datetime.now()).date()-dttt.date()).days)
		if ( dff_sl > 0 ) and (dff_tm >= 1):
            # loop to read the new entryes !! only less the 24 can be read !!!! 
			for k in range(dff_sl):
				item_cur = bs3.select('.wt-grid__item-md-4')[k]
				#### item page request#####
				pr_id= item_cur['data-listing-id']
				url2 = f'https://www.etsy.com/in-en/listing/{pr_id}'
				page2_cur = requests.get(url2,headers=headers)
				if page2_cur.status_code == requests.codes.ok:
					bs3_cur = BeautifulSoup(page2_cur.content,'lxml')
				    # final entry
					get_sales_item_details(item_cur,bs3_cur,brnd_cur,location_cur,next_url, total_sold_cur[0], number_of_reviews_cur)
			# updating the exesting csv file 
			table_cur = pd.DataFrame(data, columns=['Date-Time', 'Seller-Name', 'Seller-Location', 'URL','Product-Name', 'price', 'varients', 'size', 'People-Cart-Details', 'Total-Sales-As-Of','total-reviews'])
			table_cur.index = table_cur.index+1
			(table_cur.iloc[::-1]).to_csv(pat,sep=',', encoding='utf-8', index=False , mode='a', header=False )
			print('scraping updated results done.')
		else:
			print('Your Sheet is Already updated!')
			


# if csv exists it updates or runns the first time script
def new_or_update(band):
	fl_name = band+'_etsy.csv'
	path = os.path.join(os.path.dirname(__file__),'csv',fl_name) # path currentFolder/csv/__file__
	if os.path.isfile(path):
		with open(path,'r') as et:
            # reading csv with pandas
			reader = pd.read_csv(et,encoding='utf-8',header=0)
			sold_unit = reader['Total-Sales-As-Of'][int(reader.shape[0])-1]
			dt_tt = datetime.strptime(reader['Date-Time'][int(reader.shape[0])-1], '%Y-%m-%d %H:%M:%S.%f')
			parse_page_update(search_url,sold_unit,dt_tt,path)
	else:
		parse_page_1st(search_url,path)

	
new_or_update(band_name)
