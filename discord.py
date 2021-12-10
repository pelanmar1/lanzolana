import discord_notify as dn
import pandas as pd
from texttable import Texttable


def coin_data_to_table(data):
    table = Texttable(0)
    output_rows = [["symbol", "price"]]
    for index, row in data.iterrows():
        url = "https://www.coingecko.com/%s" % ""
        symbol = "[%s](%s)" % (row["symbol"], url)
        price = row["price"]
        output_rows.append([symbol, price])
    table.add_rows(output_rows)
    return table.draw()

def coin_data_to_list(data):
    output_string = ""
    for index, row in data.iterrows():
        url = "https://www.coingecko.com/%s" % ""
        symbol = "[%s](%s)" % (row["symbol"], url)
        output_string += "- %s \n" % symbol
    return output_string


discord_webhook_url = "https://discordapp.com/api/webhooks/918608379348398124/2fDGUSevhYI0u2wKXfvXZ7JHWfrIKL06uG5LKbIO81iUNFPcsdQ2SEbvQ86tZZfwj00S"
bots_bunny = "https://discordapp.com/api/webhooks/918612265031303229/-O45HHzfBWHZPFoHHz6wkSNIpnvIRiRoXqpCZzj8QD55HBaz-1XpgAH4KFhhcb7f14zJ"
notifier = dn.Notifier(discord_webhook_url)


data = pd.read_csv("coin_data.csv")
temp = data.head(3)

message = coin_data_to_list(temp)

notifier.send(message, print_message=False)
