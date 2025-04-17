import unittest
from src.scraper.product_scraper import ProductScraper

class TestProductScraper(unittest.TestCase):

    def setUp(self):
        self.scraper = ProductScraper()

    def test_scrape_product_details(self):
        url = 'https://example.com/product/1'
        details = self.scraper.scrape_product_details(url)
        self.assertIn('name', details)
        self.assertIn('price', details)

    def test_scrape_all_products(self):
        url = 'https://example.com/products'
        products = self.scraper.scrape_all_products(url)
        self.assertGreater(len(products), 0)

if __name__ == '__main__':
    unittest.main()