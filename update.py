from bs4 import BeautifulSoup
import requests
import lxml
import pandas as pd
from datetime import datetime
import os
import math

# Step 1: Import the necessary libraries

band_name = 'sprintervanshop'  # Step 2: Set the band name
fl_name = band_name+'_etsy.csv'
path = os.path.join(os.path.dirname(__file__),'csv',fl_name)  # Step 3: Set the path for the CSV file

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

# Step 6: Append item details to the data dictionary
def append_details_to_data(brnd, location, next_url, title, cost, drop_list, sze, Cart_Details, total_sold, number_of_reviews):
    data['Date-Time'].append(datetime.now())
    data['Seller-Name'].append(brnd)
    data['Seller-Location'].append(location)
    data['URL'].append(next_url)
    data['Product-Name'].append(title)
    data['price'].append(cost)
    data['varients'].append(drop_list)
    data['size'].append(sze)
    data['People-Cart-Details'].append(Cart_Details)
    data['Total-Sales-As-Of'].append(total_sold)
    data['total-reviews'].append(number_of_reviews)

# Step 8: Scrape details of all items on the sold page
def scrap_sold_page_items(bs, next_url):
    total_sold = ((bs.find('div', class_='hide-xs text-gray-lightest text-smaller ml-xs-2').text).strip()).split(' ')
    number_of_reviews = ((bs.find('span', class_='vertical-align-top').text).strip())[1:4]
    brnd, location = list((i.text).strip() for i in bs.findAll('div', class_='hide-xs hide-sm'))
    for item in bs.select('.wt-grid__item-md-4'):
        title = item.select('h3')[0].get_text().strip()
        try:
            Cart_Details = (item.find('div', class_='wt-text-brick wt-text-caption wt-pt-xs-1').text).strip()
        except:
            Cart_Details = None
        scrap_peritem_detail(item, brnd, title, Cart_Details, location, next_url, total_sold, number_of_reviews)

# Step 9: Scrape details of a specific item on the sold page when a limited number of cards are present
def scrap_sold_page_items_limited(bs, next_url, indx):
    total_sold = ((bs.find('div', class_='hide-xs text-gray-lightest text-smaller ml-xs-2').text).strip()).split(' ')
    number_of_reviews = ((bs.find('span', class_='vertical-align-top').text).strip())[1:4]
    brnd, location = list((i.text).strip() for i in bs.findAll('div', class_='hide-xs hide-sm'))
    item = bs.select('.wt-grid__item-md-4')[indx]
    title = item.select('h3')[0].get_text().strip()
    try:
        Cart_Details = (item.find('div', class_='wt-text-brick wt-text-caption wt-pt-xs-1').text).strip()
    except:
        Cart_Details = None
    scrap_peritem_detail(item, brnd, title, Cart_Details, location, next_url, total_sold, number_of_reviews)

# Step 13: Determine whether to run first-time scraping or update the existing CSV file
def new_or_update(next_url, pat):
    page = requests.get(next_url, headers=headers)
    if page.status_code == requests.codes.ok:
        main_bs = BeautifulSoup(page.content, 'lxml')
        if os.path.isfile(pat):
            read_existing_csv(pat, main_bs, next_url)
        else:
            scrap_sold_page_items(main_bs, next_url)
            next_page_loop_first_time(main_bs)

# Remaining functions and steps omitted for brevity

# Call the new_or_update function to start scraping or updating the CSV file
new_or_update(search_url, path)
