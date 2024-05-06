import configparser

config = configparser.ConfigParser()
config.read('tgbot/data/settings.ini')

config = config['settings']
token = config['token']
second_token = config['second_token']

allowed_id = int(config['allowed_id'])

web_server_host = config['web_server_host']
web_server_port = config['port']
webhook_url = web_server_host + '/hook'

trading_bot = config['trading_bot']
notif_bot = config['notif_bot']
