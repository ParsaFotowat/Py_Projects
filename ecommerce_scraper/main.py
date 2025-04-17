import requests
from bs4 import BeautifulSoup

url = 'https://example.com/products'
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

for product in soup.select('.product'):
    name = product.select_one('.product-name').text
    price = product.select_one('.product-price').text
    print(f'{name}: {price}')
