import configparser

config = configparser.ConfigParser()
config.read('tgbot/data/settings.ini')

config = config['settings']
token = config['token']

admin_ids = [int(i) for i in config['admin_id'].split(',')]

database_path = 'sqlite:///tgbot/data/database.db'

web_server_host = config['web_server_host']
web_server_port = 8081
webhook_url = web_server_host + '/hook'
