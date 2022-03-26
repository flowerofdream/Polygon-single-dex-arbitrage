import json
from web3.providers.rpc import HTTPProvider
from web3 import Web3

config = json.load(open('config.json'))

is_init_load = config['is_init_load']
database_name = config['database_name']
network = config['network']

http_addr = config[network]['http']
w3 = Web3(HTTPProvider(http_addr, request_kwargs={'timeout': 6000}))

usdc = config['usdc'][network]
ycrv = config['ycrv'][network]
weth = config['weth'][network]
usdt = config['usdt'][network]
dai = config['dai'][network]
yycrv = w3.toChecksumAddress("0x199ddb4bdf09f699d2cf9ca10212bd5e3b570ac2")

basicTokens = {
    'weth': {
        'address': weth,
        'symbol': 'WETH',
        'decimal': 18,
    },
    'usdt': {
        'address': usdt,
        'symbol': 'USDT',
        'decimal': 6,
    },
    'usdc': {
        'address': usdc,
        'symbol': 'USDC',
        'decimal': 6,
    },
    'dai': {
        'address': dai,
        'symbol': 'DAI',
        'decimal': 18,
    },
}

http_provider_url = config[network]['http']
pair_select_num = config['pair_num']
startToken = basicTokens[config['start']]
maxHops = config['maxHops']
minProfit = config['minProfit']