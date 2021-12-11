import discord_notify as dn

def send_discord_notification(message, webhook_url):
    notifier = dn.Notifier(webhook_url)
    print("Sending message to %s" % webhook_url)
    notifier.send(message, print_message=False)


def coin_data_to_list(data):
    output_string = "Nuevas monedas de Solana: \n"
    for index, row in data.iterrows():
        symbol = "[%s](%s)" % (row["symbol"], row["url"])
        output_string += "- %s \n" % symbol
    return output_string
