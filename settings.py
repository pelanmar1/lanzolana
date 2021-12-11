from os.path import exists
import json
import validators
import json 

CONFIG_FILENAME = "config.json"
DEFAULT_CONFIG = {
            "discordWebhookUrl": "<YOUR DISCORD WEBHOOK URL>",
            "minutesBetweenEachRun": 1
        }


def validate_config(config):
    if config is None or not isinstance(config, dict):
        raise TypeError("The provided configuration object is not valid.")
    
    if "discordWebhookUrl" in config:
        is_valid_url = validators.url(config["discordWebhookUrl"])
        if not is_valid_url:
            raise TypeError("Value for 'discordWebhookUrl' in config.json is not a valid URL.")
    else:
        raise TypeError("Value for 'discordWebhookUrl' is missing in config.json.")

    if "minutesBetweenEachRun" in config:
        time_interval = config["minutesBetweenEachRun"]
        is_valid_value = isinstance(time_interval, int)
        if not is_valid_value:
            raise TypeError("Value for 'minutesBetweenEachRun' in config.json should be a number.")
        if time_interval <=0:
            raise TypeError("Value for 'minutesBetweenEachRun' in config.json should be greater than 0.")
    else:
        raise TypeError("Value for 'minutesBetweenEachRun' is missing in config.json.")


def load_config():
    config = None
    if not exists(CONFIG_FILENAME):
        with open(CONFIG_FILENAME, 'w') as f:
            json.dump(DEFAULT_CONFIG, f, sort_keys = True, indent = 4,ensure_ascii = False)
        config = DEFAULT_CONFIG
    with open(CONFIG_FILENAME) as f:
        data = json.load(f)
        config = data
    validate_config(config)
    return config

def show_title(config):
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
    print(' Current configuration: \n ' + json.dumps(config) +"\n NOTE: You can modify current settings directly in the 'config.json' file")