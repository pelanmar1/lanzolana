import requests
from bs4 import BeautifulSoup
import csv
import json 
import pandas as pd
from os.path import exists
import discord_notify as dn
from texttable import Texttable
from apscheduler.schedulers.blocking import BlockingScheduler



# ===== DATA HELPER METHODS =====
def filter_by(data, column, value):
    temp = data.copy()
    return temp[temp[column]==value]

def sort_by(data, column, ascending=False):
    temp = data.copy()
    return temp.sort_values(by=column, ascending=ascending)

def load_config():
    config_filename = "config.json"
    if not exists(config_filename):
        default_config = {
            "discordWebhookUrl": "",
            "minutesBetweenEachRun": 1
        }
        with open(config_filename, 'w') as f:
            json.dump(default_config, f, sort_keys = True, indent = 4,ensure_ascii = False)
        return default_config
    with open("config.json") as f:
        data = json.load(f)
        return data


# ===== WEB SCRAPPING ======
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


# ===== DISCORD =====

def send_discord_notification(message):
    notifier = dn.Notifier(CONFIG["discordWebhookUrl"])
    notifier.send(message, print_message=False)

def coin_data_to_table(data):
    table = Texttable(0)
    output_rows = [["symbol", "price"]]
    for index, row in data.iterrows():
        url = "https://www.coingecko.com/%s" % row["url"]
        symbol = "[%s](%s)" % (row["symbol"], url)
        price = row["price"]
        output_rows.append([symbol, price])
    table.add_rows(output_rows)
    return table.draw()

def coin_data_to_list(data):
    output_string = "Nuevas monedas de Solana: \n"
    for index, row in data.iterrows():
        url = "https://www.coingecko.com/%s" % row["url"]
        symbol = "[%s](%s)" % (row["symbol"], url)
        output_string += "- %s \n" % symbol
    return output_string


def execute_program():
    print ("============== STARTING EXECUTION ==================")
    # Variable declaration
    debug_old_coin_data_csv_path = "debug_old_coin_data.csv"
    coin_data_csv_path = "coin_data.csv"
    new_coins_csv_path = "new_coins.csv"
    new_coins_solana_csv_path = "new_coins_solana.csv"
    old_data = None


    # Check if history exists
    if exists(coin_data_csv_path):
        print("Reading history file...")
        old_data = pd.read_csv(coin_data_csv_path)
        old_data.to_csv(debug_old_coin_data_csv_path, index=False)

    # Output new coin data
    print("Pulling new data from CoinGeek...")
    new_data = pull_coin_data()
    new_data = sort_by(new_data,"price")
    print("Saving new data to file...")
    new_data.to_csv(coin_data_csv_path, index=False)

    if old_data is None:
        print("No previous coin data was found. Creating new history file and exiting.")
        print ("==================================================")
        return

    # Output all new coins
    print("Filtering out coins that already existed...")
    new_coins = find_all_new_coins(old_data, new_data)
    new_coins = sort_by(new_coins,"price")
    print("Writing new coins to file...")
    new_coins.to_csv(new_coins_csv_path, index=False)

    # Output all new Solana coins
    new_solana_coins = filter_by(new_coins,"chain","Solana")
    new_solana_coins = sort_by(new_solana_coins, "price")
    print("Writing new Solana coins to file...")
    new_solana_coins.to_csv(new_coins_solana_csv_path, index=False)

    
    if len(new_solana_coins) >0:
        message = coin_data_to_list(new_solana_coins)
        print("Sending Discord notification with new Solana coins...")
        send_discord_notification(message)
    else:
        print("No new Solana coins found.")
    print("Finished successfully.")
    print ("==================================================")

# ====== MAIN CODE =======
if __name__ == "__main__":
    CONFIG = load_config()
    scheduler = BlockingScheduler()
    minutes = CONFIG["minutesBetweenEachRun"]
    scheduler.add_job(execute_program, 'interval', minutes=minutes)
    print('''
    
 ▄            ▄▄▄▄▄▄▄▄▄▄▄  ▄▄        ▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄▄▄▄▄▄▄▄▄▄▄  ▄            ▄▄▄▄▄▄▄▄▄▄▄  ▄▄        ▄  ▄▄▄▄▄▄▄▄▄▄▄ 
▐░▌          ▐░░░░░░░░░░░▌▐░░▌      ▐░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░▌          ▐░░░░░░░░░░░▌▐░░▌      ▐░▌▐░░░░░░░░░░░▌
▐░▌          ▐░█▀▀▀▀▀▀▀█░▌▐░▌░▌     ▐░▌ ▀▀▀▀▀▀▀▀▀█░▌▐░█▀▀▀▀▀▀▀█░▌▐░▌          ▐░█▀▀▀▀▀▀▀█░▌▐░▌░▌     ▐░▌▐░█▀▀▀▀▀▀▀█░▌
▐░▌          ▐░▌       ▐░▌▐░▌▐░▌    ▐░▌          ▐░▌▐░▌       ▐░▌▐░▌          ▐░▌       ▐░▌▐░▌▐░▌    ▐░▌▐░▌       ▐░▌
▐░▌          ▐░█▄▄▄▄▄▄▄█░▌▐░▌ ▐░▌   ▐░▌ ▄▄▄▄▄▄▄▄▄█░▌▐░▌       ▐░▌▐░▌          ▐░█▄▄▄▄▄▄▄█░▌▐░▌ ▐░▌   ▐░▌▐░█▄▄▄▄▄▄▄█░▌
▐░▌          ▐░░░░░░░░░░░▌▐░▌  ▐░▌  ▐░▌▐░░░░░░░░░░░▌▐░▌       ▐░▌▐░▌          ▐░░░░░░░░░░░▌▐░▌  ▐░▌  ▐░▌▐░░░░░░░░░░░▌
▐░▌          ▐░█▀▀▀▀▀▀▀█░▌▐░▌   ▐░▌ ▐░▌▐░█▀▀▀▀▀▀▀▀▀ ▐░▌       ▐░▌▐░▌          ▐░█▀▀▀▀▀▀▀█░▌▐░▌   ▐░▌ ▐░▌▐░█▀▀▀▀▀▀▀█░▌
▐░▌          ▐░▌       ▐░▌▐░▌    ▐░▌▐░▌▐░▌          ▐░▌       ▐░▌▐░▌          ▐░▌       ▐░▌▐░▌    ▐░▌▐░▌▐░▌       ▐░▌
▐░█▄▄▄▄▄▄▄▄▄ ▐░▌       ▐░▌▐░▌     ▐░▐░▌▐░█▄▄▄▄▄▄▄▄▄ ▐░█▄▄▄▄▄▄▄█░▌▐░█▄▄▄▄▄▄▄▄▄ ▐░▌       ▐░▌▐░▌     ▐░▐░▌▐░▌       ▐░▌
▐░░░░░░░░░░░▌▐░▌       ▐░▌▐░▌      ▐░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░░░░░░░░░░░▌▐░▌       ▐░▌▐░▌      ▐░░▌▐░▌       ▐░▌
 ▀▀▀▀▀▀▀▀▀▀▀  ▀         ▀  ▀        ▀▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀▀▀▀▀▀▀▀▀▀▀  ▀         ▀  ▀        ▀▀  ▀         ▀ 
                                                                                                                     

    ''')
    print("<< Corriendo cada %d minutos >>" % minutes)
    scheduler.start()





    
