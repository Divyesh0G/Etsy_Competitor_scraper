# Etsy Sales Scraper

This is a Python script that scrapes sales data from an Etsy shop and saves it to a CSV file. The script retrieves information such as the seller name, location, product details, price, variants, and more.

## Prerequisites

Before running the script, make sure you have the following installed:

- Python (version 3.6 or higher)
- Beautiful Soup 4
- Requests
- Pandas

You can install the required Python libraries using pip:

pip install beautifulsoup4 requests pandas



## Usage

1. Clone or download the repository to your local machine.
2. Open the terminal or command prompt and navigate to the project directory.
3. Run the script using the following command:

python etsy_sales_scraper.py


4. Enter the name of the Etsy shop you want to scrape when prompted.
5. The script will start scraping the sales data from the Etsy shop and display the progress.
6. Once the scraping is complete, the data will be saved to a CSV file in the "csv" directory.

## Configuration

- The script uses a User-Agent header to mimic a web browser. You can modify the User-Agent value in the `headers` variable if needed.
- The script saves the CSV file with the name "{band_name}_etsy.csv" in the "csv" directory. You can change the directory or file name by modifying the `fl_name` and `path` variables in the code.

## Contributing

Contributions are welcome! If you encounter any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License

This project is licensed under the [MIT License](LICENSE).
