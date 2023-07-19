from bs4 import BeautifulSoup
import requests
import lxml
import pandas as pd
from datetime import datetime
import os
import math

band_name = 'sprintervanshop'#input('Please, enter a band name:\n')
fl_name = band_name+'_etsy.csv'
path = os.path.join(os.path.dirname(__file__),'csv',fl_name) # path currentFolder/csv/__file__

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






def append_details_to_data(brnd,location,next_url,title,cost,drop_list,sze,Cart_Details,total_sold,number_of_reviews):
    # Store the values into the 'data' object
	data['Date-Time'].append(datetime.now())
	data['Seller-Name'].append(brnd)#
	data['Seller-Location'].append(location)#
	data['URL'].append(next_url)#
	data['Product-Name'].append(title)
	data['price'].append(cost)#
	data['varients'].append(drop_list)#
	data['size'].append(sze)#
	data['People-Cart-Details'].append(Cart_Details)
	data['Total-Sales-As-Of'].append(total_sold)#
	data['total-reviews'].append(number_of_reviews)#




def scrap_peritem_detail(item,brnd,title,Cart_Details,location,next_url,total_sold,number_of_reviews):
    #### item page request#####
    pr_id= item['data-listing-id']
    pr_url = f'https://www.etsy.com/in-en/listing/{pr_id}'
    get_pr_page = requests.get(pr_url,headers=headers)
    if get_pr_page.status_code == requests.codes.ok:
        pr_bs = BeautifulSoup(get_pr_page.content,'lxml')
        # price
        try:
            cost = (pr_bs.find('p',class_='wt-text-title-03 wt-mr-xs-2').text).strip()
        except:
            cost = 'Sorry, this item is sold out'
    
        # varients
        try:
            drop_list = ','.join([ (x.text).strip() for x in (pr_bs.find('div',class_='wt-select 0-selector-container')).findAll('option')][1:])
        except:
            drop_list = None

        # size
        try:
            sze = ','.join([(x.text).strip() for x in (pr_bs.find('div',class_='wt-select 1-selector-container')).findAll('option')][1:])
        except:
            sze = None
        append_details_to_data(brnd,location,next_url,title,cost,drop_list,sze,Cart_Details,total_sold[0],number_of_reviews)
        


def scrap_sold_page_items(bs,next_url):
    ####scrapping data from table#####
    # list_all_cards = bs.find('div',class_='js-merch-stash-check-listing')
    # Favourite_shop = bs.find("span", {"data-region":"num-favorers"})
    total_sold = ((bs.find('div',class_='hide-xs text-gray-lightest text-smaller ml-xs-2').text).strip()).split(' ')
    number_of_reviews = ((bs.find('span',class_='vertical-align-top').text).strip())[1:4]
    brnd,location = list((i.text).strip() for i in  bs.findAll('div', class_='hide-xs hide-sm'))
    # loop for every item on sold page
    for item in bs.select('.wt-grid__item-md-4'):
        title = item.select('h3')[0].get_text().strip()
	    # cart details
        try:
            Cart_Details = (item.find('div', class_='wt-text-brick wt-text-caption wt-pt-xs-1').text).strip()
        except:
            Cart_Details = None
        scrap_peritem_detail(item,brnd,title,Cart_Details,location,next_url,total_sold,number_of_reviews)
    


def scrap_sold_page_items_limited(bs,next_url,indx):
    ####scrapping data from table#####
    # list_all_cards = bs.find('div',class_='js-merch-stash-check-listing')
    # Favourite_shop = bs.find("span", {"data-region":"num-favorers"})
    total_sold = ((bs.find('div',class_='hide-xs text-gray-lightest text-smaller ml-xs-2').text).strip()).split(' ')
    number_of_reviews = ((bs.find('span',class_='vertical-align-top').text).strip())[1:4]
    brnd,location = list((i.text).strip() for i in  bs.findAll('div', class_='hide-xs hide-sm'))
    # loop for every item on sold page
    item = bs.select('.wt-grid__item-md-4')[indx]
    title = item.select('h3')[0].get_text().strip()
    # cart details
    try:
        Cart_Details = (item.find('div', class_='wt-text-brick wt-text-caption wt-pt-xs-1').text).strip()
    except:
        Cart_Details = None
    scrap_peritem_detail(item,brnd,title,Cart_Details,location,next_url,total_sold,number_of_reviews)


# def bs_page(next_url):
#     page = requests.get(next_url,headers=headers)
# 	# check
#     if page.status_code == requests.codes.ok:
# 		sold_bs = BeautifulSoup(page.content,'lxml')
#         scrap_sold_page_items(sold_bs,next_url)

#     else:
#         print('Error_bs_page')


def next_page_loop_first_time(sold_bs):
    try:	
        next_page_text = sold_bs.find('ul', class_='btn-group-md list-unstyled text-left').findAll('li')[-1]['class'][-1]
        if next_page_text == 'btn-group-item-md':
            next_page_partial = sold_bs.find('ul', class_='btn-group-md list-unstyled text-left').findAll('li')[-1].find('a')['href']
            new_or_update(next_page_partial,path)
        else:
            pass
    except:
        pass




def read_existing_csv(path,bs,next_url):
    # reading csv with pandas
    reader = pd.read_csv(path,encoding='utf-8',header=0)
    # old sold units
    old_sold_unit = reader['Total-Sales-As-Of'][int(reader.shape[0])-1]
    total_sold_cur = ((bs.find('div',class_='hide-xs text-gray-lightest text-smaller ml-xs-2').text).strip()).split(' ')
    # ## check diff  loop only runs if the diff in sold items if more the 1 and  diff in days of runnung script is more then 1##
    dff_sl =  int(total_sold_cur[0]) - int(old_sold_unit)
    
    number_of_page_to_scrape = math.ceil(dff_sl/24)
    
    number_of_card_to_scrape_on_last_page = dff_sl-(24*number_of_page_to_scrape)

    # ### date time diff
    dt_tt = datetime.strptime(reader['Date-Time'][int(reader.shape[0])-1], '%Y-%m-%d %H:%M:%S.%f')
    dff_tm = int(((datetime.now()).date()-dt_tt.date()).days)
    if dff_tm >= 1:
        while number_of_page_to_scrape > 1:
            for i in range(number_of_page_to_scrape-1):
                url_spec = f'https://www.etsy.com/in-en/shop/{band_name}/sold/{i}'
                scrap_sold_page_items(bs,url_spec)
            number_of_page_to_scrape -= (number_of_page_to_scrape-1)
            # add pd update
        else:
            if number_of_card_to_scrape_on_last_page == 0:
                scrap_sold_page_items(bs,next_url)
                # add pd update 
            else:
                for k in range(number_of_card_to_scrape_on_last_page):
                    scrap_sold_page_items_limited(bs,next_url,k)
                     # add pd update


    #     loop_for_update(bs,sold_unit)
    else:
        print('Your Sheet is Already updated!')


# def bs_update(next_url):
#     pass


def new_or_update(next_url,pat):
    page = requests.get(next_url,headers=headers)
	# check
    if page.status_code == requests.codes.ok:
        main_bs = BeautifulSoup(page.content,'lxml')
        if os.path.isfile(pat):
            read_existing_csv(pat,main_bs,next_url)
        else:
            scrap_sold_page_items(main_bs,next_url)
            next_page_loop_first_time(main_bs)


new_or_update(search_url,path)


###########################################





