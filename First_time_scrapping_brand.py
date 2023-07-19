from bs4 import BeautifulSoup
import requests
import lxml
import pandas as pd
from datetime import datetime

# Get the band name from user input
band_name = input('Please enter a band name:\n')

# Print a message indicating the start of the search
print()
print(f'Searching {band_name}. Please wait...')
print()

# Set the base URL and construct the search URL
base_url = 'https://www.etsy.com'
search_url = f'https://www.etsy.com/in-en/shop/{band_name}/sold/'

# Initialize the data dictionary to store scraped details
data = {
    'Date-Time': [],
    'Seller-Name': [],
    'Seller-Location': [],
    'URL': [],
    'Product-Name': [],
    'People-Cart-Details': [],
    'Total-Sales-As-Of': [],
    'total-reviews': [],
}


def export_table_and_print(data):
    # Create a DataFrame from the data dictionary
    table = pd.DataFrame(data, columns=['Date-Time', 'Seller-Name', 'Seller-Location', 'URL', 'Product-Name', 'People-Cart-Details', 'Total-Sales-As-Of', 'total-reviews'])
    table.index = table.index + 1
    # Export the DataFrame to a CSV file (if needed)
    # table.to_csv(f'{band_name}_albums.csv', sep=',', encoding='utf-8', index=False)
    # Print the scraped results
    print('Scraping done. Here are the results:')
    print(table)


def get_sales_item_details(soup, brnd, location, link, number_sold, number_of_reviews):
    # Extract details from individual cards
    title = soup.select('h3')[0].get_text().strip()
    try:
        Cart_Details = (soup.find('div', class_='wt-text-brick wt-text-caption wt-pt-xs-1').text).strip()
    except:
        Cart_Details = None
    # Store the values into the 'data' object
    data['Date-Time'].append(datetime.now())
    data['Seller-Name'].append(brnd)
    data['Seller-Location'].append(location)
    data['URL'].append(link)
    data['Product-Name'].append(title)
    data['People-Cart-Details'].append(Cart_Details)
    data['Total-Sales-As-Of'].append(number_sold)
    data['total-reviews'].append(number_of_reviews)


def parse_page(next_url):
    # Set the User-Agent header for the HTTP request
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_2) AppleWebKit/601.3.9 (KHTML, like Gecko) Version/9.0.2 Safari/601.3.9'}
    
    # Send an HTTP GET request to the next URL
    page = requests.get(next_url, headers=headers)
    
    # Check if the request was successful
    if page.status_code == requests.codes.ok:
        bs = BeautifulSoup(page.content, 'lxml')
        
        # Fetch the total number of sold items and the number of reviews
        total_sold = ((bs.find('div', class_='hide-xs text-gray-lightest text-smaller ml-xs-2').text).strip()).split(' ')
        number_of_reviews = ((bs.find('span', class_='vertical-align-top').text).strip())[1:4]
        
        # Get the brand and location information
        brnd, location = list((i.text).strip() for i in bs.findAll('div', class_='hide-xs hide-sm'))
        
        # Find all the sales item cards
        list_all_cards = bs.findAll('div', class_='js-merch-stash-check-listing')
        
        # Iterate over each sales item card and extract details
        for item in bs.select('.wt-grid__item-md-4'):
            get_sales_item_details(item, brnd, location, next_url, total_sold[0], number_of_reviews)
        
        try:
            # Check if there is a next page
            next_page_text = bs.find('ul', class_='btn-group-md list-unstyled text-left').findAll('li')[-1]['class'][-1]
            if next_page_text == 'btn-group-item-md':
                # Get the URL for the next page
                next_page_partial = bs.find('ul', class_='btn-group-md list-unstyled text-left').findAll('li')[-1].find('a')['href']
                parse_page(next_page_partial)
            else:
                # Export the table and print the results
                export_table_and_print(data)
        except:
            # Export the table and print the results
            export_table_and_print(data)


# Start parsing from the initial search URL
parse_page(search_url)
