#!/usr/bin/env python

'''
fetch a url and grab a div with class "rates" 
'''
from io import StringIO
import csv 
import logging
import requests

from bs4 import BeautifulSoup

fd_url = {
    'hdfc': 'https://www.hdfcbank.com/personal/save/deposits/fixed-deposit-interest-rate',
    'icici': 'https://www.icicibank.com/personal-banking/deposits/fixed-deposit/fd-interest-rates'
}


# get the table html node for the bank
def get_table_node(soup: BeautifulSoup, bankname: str):
    if bankname == 'icici':
        return soup.find('div', {'class': 'main-contentz'}).find('table')
    elif bankname == 'hdfc':
        return soup.find('table', {'class': 'rates-table-main'})
    else:
        raise Exception('Bank not supported')

# get fd rates for icici
def get_rates(bankname: str):
    url = fd_url[bankname]

    # request with a chrome user agent
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    rates = get_table_node(soup, bankname)

    # convert the html node rates to csv
    headers = [th.text.strip() for th in rates.select("tr th")[-1]]

    # Convert html table to csv
    csv_text = ''
    with StringIO() as dataio:
        wr = csv.writer(dataio)
        # wr.writerow(headers)
        wr.writerows([[td.text.strip() for td in row.find_all("td")] for row in rates.select("tr")])
        csv_text = dataio.getvalue()
   
    return csv_text

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    logging.info('Fetching rates for ICICI')
    print(get_rates('icici'))
    logging.info('Fetching rates for ICICI')
    print(get_rates('hdfc'))
    logging.info('Fetching rates for SBI')
    print(get_rates('SBI'))