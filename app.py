
import pandas as pd
from os.path import exists
from web_scrapping import pull_coin_data, find_all_new_coins
from data_helpers import sort_by, filter_by
from discord_utils import send_discord_notification, coin_data_to_list
from settings import load_config, show_title
import os

CONFIG = load_config()

def execute():
    show_title(CONFIG)
    print ("============== STARTING EXECUTION ==================")
    # Variable declaration
    resources_dir = "data"
    os.makedirs(resources_dir, exist_ok=True)
    debug_old_coin_data_csv_path = "data/debug_old_coin_data.csv"
    coin_data_csv_path = "data/coin_data.csv"
    new_coins_csv_path = "data/new_coins.csv"
    new_coins_solana_csv_path = "data/new_coins_solana.csv"
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
        send_discord_notification(message,CONFIG["discordWebhookUrl"])
    else:
        print("No new Solana coins found.")
    print("Finished successfully.")
    print ("==================================================")
