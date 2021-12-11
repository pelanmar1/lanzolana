import requests
from bs4 import BeautifulSoup
import pandas as pd

def parse_coin(row):
    cols = row.findAll('td')
    coin = {}
    coin["coin"] = cols[2].findAll('a')[0].text.strip() if len(cols[2].findAll('a'))>0 else "N/A"
    coin["symbol"] = cols[2].findAll('a')[1].text.strip() if len(cols[2].findAll('a'))>1 else "N/A"
    coin["price"] = cols[3].find('span').text.strip() if cols[3].find('span') else "N/A"
    coin["chain"] = cols[4].attrs["data-sort"]
    coin["1h"] = cols[5].attrs["data-sort"]
    coin["24h"] = cols[6].attrs["data-sort"] 
    coin["24hVolume"] = cols[7].find('span').text.strip() if cols[7].find('span') else "N/A"
    coin["fdv"] = cols[8].text.strip()
    coin["numOfHolders"] = cols[9].text.strip()
    coin["holderChange"] = cols[10].text.strip()
    coin["lastAdded"] = cols[11].text.strip()
    coin["url"] = ("https://www.coingecko.com/%s" % cols[2].findAll('a')[0].attrs["href"]) if len(cols[2].findAll('a'))>0 else "N/A"
    
    return coin

def pull_coin_data():
    BASE_URL = "https://www.coingecko.com/en/coins/recently_added"
    # To get all data we need to pull data from all 5 pages of the table
    urls = ["%s?page=%d" % (BASE_URL, i) for i in range(1,5,1)] 

    coins = []
    for url in urls:
        r = requests.get(url)
        soup = BeautifulSoup(r.content, 'html5lib')
        table = soup.find('table', attrs = {'data-target':'gecko-table.table portfolios-v2.table'}) 
        rows = table.findAll('tr')[1:] # We skip the header row
        coins = coins + [parse_coin(row) for row in rows]
    if len(coins)>0:
        return pd.DataFrame(coins)
    return None

def find_all_new_coins(old_data, new_data):
    compare_by_col = "symbol"
    # Find new coins
    merged_data = old_data.merge(new_data, on=compare_by_col, how="right", indicator=True)
    new_coins = merged_data[merged_data["_merge"]=="right_only"]
    # Clean columns
    columns_of_interest = [compare_by_col] + [col for col in new_coins.columns if col.endswith('_y')]
    new_coins = new_coins[columns_of_interest]
    # Remove suffix from columns
    new_coins.columns = new_coins.columns.str.rstrip("_y")
    return new_coins
