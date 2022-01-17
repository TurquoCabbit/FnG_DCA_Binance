from time import sleep
import sys
import os

from client import Client_Spot

client = Client_Spot(test_net = True, api_key = sys.argv[2], api_secret = sys.argv[3], url = 'https://testnet.binance.vision')

base = sys.argv[1].upper()
coin = base + 'USDT'
balance = client.query_balance(coin)
print('{} free balance : {}'.format(base, balance[base]['free']))
sleep(0.2)

client.place_market_order_base(coin, 'sell', float(balance[base]['free']))
sleep(0.2)

balance_1 = client.query_balance(coin)
print('{} result balance : {}'.format(base, balance_1[base]['free']))

os.system('pause')
os._exit(0)