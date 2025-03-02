import requests
from bs4 import BeautifulSoup


def get_nse_symbols():

    url = "https://en.wikipedia.org/wiki/List_of_companies_listed_on_the_National_Stock_Exchange_of_India"

    def valid_symbol(symbol):
        return all(c.isupper() or c.isdigit() for c in symbol)

    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')
    stock_symbols = []
    for link in soup.find_all('a', class_='external text'):
        symbol = link.text.strip()
        if symbol and valid_symbol(symbol):
            stock_symbols.append(symbol)

    return stock_symbols
