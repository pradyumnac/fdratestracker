#!/usr/bin/env python

'''
Fetch Latest FD rates for various banks
'''
from io import StringIO
import csv 
import logging
import requests

import asyncio

from bs4 import BeautifulSoup
from pytablewriter import UnicodeTableWriter

bank_urls = {
    'hdfc': 'https://www.hdfcbank.com/personal/save/deposits/fixed-deposit-interest-rate',
    'icici': 'https://www.icicibank.com/personal-banking/deposits/fixed-deposit/fd-interest-rates',
    'sbi': 'https://sbi.co.in/web/interest-rates/deposit-rates/retail-domestic-term-deposits', 
    'uco': 'https://www.ucobank.com/english/interest-rate-deposit-account.aspx'
}

rate_tables = {

}

# get the table html node for the bank
def get_table_node(soup: BeautifulSoup, bankname: str):
    if bankname == 'icici':
        return soup.find('div', {'class': 'main-contentz'}).find('table')
    elif bankname == 'hdfc':
        return soup.find('table', {'class': 'rates-table-main'})
    elif bankname == 'sbi':
        return soup.find('div', {'class': 'featureList'}).find('table')
    elif bankname == 'uco':
        return soup.find_all('table', {'class': 'table'})[1]
    else:
        raise Exception('Bank not supported')

# get fd rates for icici
async def get_rates(bankname: str):
    url = bank_urls[bankname]

    # request with a chrome user agent
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, 'lxml')
    rates = get_table_node(soup, bankname)

    # convert the html node rates to csv
    # headers = [th.text.strip() for th in rates.select("tr th")[-1]]

    # Convert html table to csv
    rows = [[td.text.strip() for td in row.find_all("td")] for row in rates.select("tr")]
    
    rate_tables[bankname] = rows

async def main():
    tasks = []
    for bank in bank_urls.keys():
        task = asyncio.create_task(get_rates(bank))
        tasks.append(task)
    await asyncio.gather(*tasks)
    
    # print the rate tables
    for bank in rate_tables:
        print('--' * 10+' '+bank+' '+ '--' * 10)
        writer = UnicodeTableWriter(
            table_name=f'# {bank}',
            value_matrix=rate_tables[bank],
        )
        writer.write_table()

def run():
    asyncio.run(main())

if __name__ == '__main__':
    run()
