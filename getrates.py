#!/usr/bin/env python

'''
Fetch Latest FD rates for various banks
'''
import datetime
import json
import os
import requests

import asyncio

from bs4 import BeautifulSoup
from pytablewriter import UnicodeTableWriter

bank_urls = {
    'hdfc': 'https://www.hdfcbank.com/personal/save/deposits/fixed-deposit-interest-rate',
    'icici': 'https://www.icicibank.com/personal-banking/deposits/fixed-deposit/fd-interest-rates',
    'sbi': 'https://sbi.co.in/web/interest-rates/deposit-rates/retail-domestic-term-deposits', 
    'uco': 'https://www.ucobank.com/english/interest-rate-deposit-account.aspx',
    'kotak': 'https://www.kotak.com/en/rates/interest-rates.html', # TODO
    'indusind': 'https://www.indusind.com/in/en/personal/rates.html', # TODO
    'idfc': 'https://www.idfcfirstbank.com/personal-banking/deposits/fixed-deposit/fd-interest-rates', # TODO
    'pnb': 'https://www.pnbindia.in/Interest-Rates-Deposit.html', # TODO
    'unionbank': 'https://www.unionbankofindia.co.in/english/interest-rate.aspx', # TODO
    'yesbank': 'https://www.yesbank.in/personal-banking/yes-individual/deposits/fixed-deposit', # TODO
    'indianbank': 'https://www.indianbank.in/departments/deposit-rates/#!', # TODO
    'indianoverseas': 'https://www.iob.in/Domestic_Rates', # TODO
    'canarabank': 'https://canarabank.com/User_page.aspx?othlink=9', # TODO
    'bankofbaroda': 'https://www.bankofbaroda.in/interest-rate-and-service-charges/deposits-interest-rates', # TODO
    'bankofmaharashtra': 'https://bankofmaharashtra.in/domestic-term-deposits', # TODO
    'bankofindia': 'https://bankofindia.co.in/interest-rates-on-deposits', # TODO
    'centralbank': 'https://www.centralbankofindia.co.in/en/interest-rates-on-deposit', # TODO
    'dhanlaxmibank': 'https://www.dhanbank.com/interest-rates/', # TODO
    'dbs': 'https://www.dbs.com/in/treasures/common/interest-rates.page', # TODO
    'federalbank': 'https://www.federalbank.co.in/deposit-rate', # TODO
    'equitasbank': 'https://www.equitasbank.com/fixed-deposit', # TODO
    'ujjivanbank': 'https://www.ujjivansfb.in/support-interest-rates', # TODO
    # 'axis': 'https://www.axisbank.com/docs/default-source/interest-rates-new/fixed-deposit-wef-29-03-2023.pdf', # TODO
    # 'allahabadbank': '', # Meged with Indian bank
    # 'corporationbank': '', # merged with union bank

}

rate_tables = {}

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
    elif bankname == 'kotak':
        pass
    elif bankname == 'indusind':
        pass
    elif bankname == 'idfc':
        pass
    elif bankname == 'pnb':
        pass
    elif bankname == 'unionbank':
        pass
    elif bankname == 'yesbank':
        pass
    elif bankname == 'indianbank':
        pass
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
    
    # remove row fron rows if all of its members are empty
    rows = [row for row in rows if any(row)]

    # if bankname == 'uco', remove top two ros
    if bankname == 'uco':
        rows = rows[2:]
    rate_tables[bankname] = rows

def save():
    today = datetime.datetime.now().strftime('%Y/%m/%d')
    filepath = f'data/{today}.json'
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    json.dump(rate_tables, open(filepath, 'w'))

async def main():
    tasks = []
    for bank in bank_urls.keys():
        task = asyncio.create_task(get_rates(bank))
        tasks.append(task)
    await asyncio.gather(*tasks)
    
    # Output/Save Rates
    save()

    # print the rate tables
    # rates = {}
    # for bank in rate_tables:
    #     rates[bank] = rate_tables[bank]
        # print('--' * 10+' '+bank+' '+ '--' * 10)
        # writer = UnicodeTableWriter(
        #     table_name=f'# {bank}',
        #     value_matrix=rate_tables[bank],
        # )
        # writer.write_table()

if __name__ == '__main__':
    asyncio.run(main())
