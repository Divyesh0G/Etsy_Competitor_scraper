from bs4 import BeautifulSoup
import requests
import lxml
import pandas as pd
from datetime import datetime
import os

# Get the band name from user input
band_name = input('Please enter a band name:\n')

# Print a message indicating the start of the search
print()
print(f'Searching {band_name}. Please wait...')
print()

# Set the base URL and construct the search URL
base_url = 'https://www.etsy.com'
search_url = f'https://www.etsy.com/in-en/shop/{band_name}/sold'
headers = {'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'}

# Initialize the data dictionary to store scraped details
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

# Save the data from the data dictionary to a CSV file
def export_table_and_print(data, path):
    table = pd.DataFrame(data, columns=['Date-Time', 'Seller-Name', 'Seller-Location', 'URL', 'Product-Name', 'price', 'varients', 'size', 'People-Cart-Details', 'Total-Sales-As-Of', 'total-reviews'])
    table.index = table.index + 1
    (table.iloc[::-1]).to_csv(path, sep=',', encoding='utf-8', index=False)
    print('Scraping done.')

# Extract details from each sales item
def get_sales_item_details(soup, bs2, brnd, location, link, number_sold, number_of_reviews):
    title = soup.select('h3')[0].get_text().strip()
    try:
        Cart_Details = (soup.find('div', class_='wt-text-brick wt-text-caption wt-pt-xs-1').text).strip()
    except:
        Cart_Details = None
    try:
        cost = (bs2.find('p', class_='wt-text-title-03 wt-mr-xs-2').text).strip()
    except:
        cost = 'Sorry, this item is sold out'
    try:
        drop_list = ','.join([(x.text).strip() for x in (bs2.find('div', class_='wt-select 0-selector-container')).findAll('option')][1:])
    except:
        drop_list = None
    try:
        sze = ','.join([(x.text).strip() for x in (bs2.find('div', class_='wt-select 1-selector-container')).findAll('option')][1:])
    except:
        sze = None
    data['Date-Time'].append(datetime.now())
    data['Seller-Name'].append(brnd)
    data['Seller-Location'].append(location)
    data['URL'].append(link)
    data['Product-Name'].append(title)
    data['price'].append(cost)
    data['varients'].append(drop_list)
    data['size'].append(sze)
    data['People-Cart-Details'].append(Cart_Details)
    data['Total-Sales-As-Of'].append(number_sold)
    data['total-reviews'].append(number_of_reviews)

# Scrape the first page and save the data to a CSV file
def parse_page_1st(next_url, path):
    page = requests.get(next_url, headers=headers)
    if page.status_code == requests.codes.ok:
        bs = BeautifulSoup(page.content, 'lxml')
        total_sold = ((bs.find('div', class_='hide-xs text-gray-lightest text-smaller ml-xs-2').text).strip()).split(' ')
        number_of_reviews = ((bs.find('span', class_='vertical-align-top').text).strip())[1:4]
        brnd, location = list((i.text).strip() for i in bs.findAll('div', class_='hide-xs hide-sm'))
        for item in bs.select('.wt-grid__item-md-4'):
            pr_id = item['data-listing-id']
            url2 = f'https://www.etsy.com/in-en/listing/{pr_id}'
            page2 = requests.get(url2, headers=headers)
            if page2.status_code == requests.codes.ok:
                bs2 = BeautifulSoup(page2.content, 'lxml')
                get_sales_item_details(item, bs2, brnd, location, next_url, total_sold[0], number_of_reviews)
        try:
            next_page_text = bs.find('ul', class_='btn-group-md list-unstyled text-left').findAll('li')[-1]['class'][-1]
            if next_page_text == 'btn-group-item-md':
                next_page_partial = bs.find('ul', class_='btn-group-md list-unstyled text-left').findAll('li')[-1].find('a')['href']
                parse_page_1st(next_page_partial, path)
            else:
                export_table_and_print(data, path)
        except:
            export_table_and_print(data, path)

# Update the existing CSV file
def parse_page_update(next_url, sold, dt_tt, path):
    page3 = requests.get(next_url, headers=headers)
    if page3.status_code == requests.codes.ok:
        bs3 = BeautifulSoup(page3.content, 'lxml')
        total_sold_cur = ((bs3.find('div', class_='hide-xs text-gray-lightest text-smaller ml-xs-2').text).strip()).split(' ')
        number_of_reviews_cur = ((bs3.find('span', class_='vertical-align-top').text).strip())[1:4]
        brnd_cur, location_cur = list((i.text).strip() for i in bs3.findAll('div', class_='hide-xs hide-sm'))
        dff_sl = int(total_sold_cur[0]) - int(sold)
        dff_tm = int(((datetime.now()).date() - dt_tt.date()).days)
        if (dff_sl > 0) and (dff_tm >= 1):
            for k in range(dff_sl):
                item_cur = bs3.select('.wt-grid__item-md-4')[k]
                pr_id = item_cur['data-listing-id']
                url2 = f'https://www.etsy.com/in-en/listing/{pr_id}'
                page2_cur = requests.get(url2, headers=headers)
                if page2_cur.status_code == requests.codes.ok:
                    bs3_cur = BeautifulSoup(page2_cur.content, 'lxml')
                    get_sales_item_details(item_cur, bs3_cur, brnd_cur, location_cur, next_url, total_sold_cur[0], number_of_reviews_cur)
            table_cur = pd.DataFrame(data, columns=['Date-Time', 'Seller-Name', 'Seller-Location', 'URL', 'Product-Name', 'price', 'varients', 'size', 'People-Cart-Details', 'Total-Sales-As-Of', 'total-reviews'])
            table_cur.index = table_cur.index + 1
            (table_cur.iloc[::-1]).to_csv(path, sep=',', encoding='utf-8', index=False, mode='a', header=False)
            print('Scraping updated results done.')
        else:
            print('Your sheet is already updated!')

# Check if the CSV file exists and decide whether to update or run the first time script
def new_or_update(band):
    fl_name = band + '_etsy.csv'
    path = os.path.join(os.path.dirname(__file__), 'csv', fl_name)
    if os.path.isfile(path):
        with open(path, 'r') as et:
            reader = pd.read_csv(et, encoding='utf-8', header=0)
            sold_unit = reader['Total-Sales-As-Of'][int(reader.shape[0])-1]
            dt_tt = datetime.strptime(reader['Date-Time'][int(reader.shape[0])-1], '%Y-%m-%d %H:%M:%S.%f')
            parse_page_update(search_url, sold_unit, dt_tt, path)
    else:
        parse_page_1st(search_url, path)

# Call the function to decide whether to update or run the first time script
new_or_update(band_name)
