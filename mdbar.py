import json
from mdapi import MDApiConnector
from configparser import ConfigParser


def get_mid(candle):
    return round((candle.get('high') + candle.get('low')) / 2, 2)

config = ConfigParser()
config.read_file(open('config.ini'))

# create connectors to API
api = MDApiConnector(
    client_id=config['API']['client_id'],
    app_id=config['API']['app_id'],
    key=config['API']['shared_key']
)

crossrates = []
singles = []

for pair in json.loads(config['Symbols']['pairs']):
    cross = api.get_crosstates(pair.split('/')[0], pair.split('/')[1])
    if type(cross) == dict:
        crossrates.append(cross.get('pair') + ':' + str(round(cross.get('rate'), 2)))

for single in json.loads(config['Symbols']['singles']):
    singles.append(single.split('.')[0] + ':' + str(get_mid(api.get_last_ohlc_bar(single))))

#print('{}:{}'.format(eur_usd.get('pair') ,eur_usd.get('rate')))

print(' '.join(crossrates), ' '.join(singles))
