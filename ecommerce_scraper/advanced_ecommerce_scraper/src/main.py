import requests
from scraper.product_scraper import ProductScraper

def main():
    url = 'https://example.com/products'
    scraper = ProductScraper()
    
    # Scrape all products from the given URL
    products = scraper.scrape_all_products(url)
    
    # Print the scraped product details
    for product in products:
        print(f"Name: {product['name']}, Price: {product['price']}")

if __name__ == "__main__":
    main()