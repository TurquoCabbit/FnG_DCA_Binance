from time import localtime
from time import strftime
from time import time
from datetime import datetime
import sys
import os
import json
import csv
from gc import collect
from shutil import rmtree
from shutil import copytree

from Make_log import Log
from Loading_animation import delay_anima
from client import Client_Spot
from fear_and_greed import crypto_fear_and_greed_alternative

os.system('cls')
##########################################################
Version = '0.1.18'
Date = '2022/02/05'

##############################################################################################################################
### init log
log = Log('log', '%Y-%m')
str = 'Bybit Fear and Greed index DCA trading bot ver {} {}'.format(Version, Date)
separator = '=' * ((len(str) - 4) // 2) + 'START' + '=' * ((len(str) - 4) // 2)
log.log(separator)
log.log_and_show(str)
del separator
del str

class CFG:
    def __init__(self, version) -> None:
        self.version = version        
        
        self.cfg_init = {
                            'Version' : version,
                            'Run_on_testnet' : True,
                            'Base' : 'BTC',
                            'Quote' : 'USDT',
                            'Duration_days' : 365,
                            'Daily_invest' : 10,
                            'Accumulate_Buy' : True,
                            'Accumulate_Sell' : False,
                            'Buy_at_fear' : 25,
                            'Sell_at_greed' : 75,
                            'Retry_times' : 30,
                            'Retry_delay' : 0.2,
                            'Polling_delay' : 600
                        }
        self.__var_init__()

    def __var_init__(self):
        self.Test_net = True
        self.Base = None
        self.Quote = None
        self.Duration_days = None
        self.Daily_invest = None
        self.Accumulate_Buy = None
        self.Accumulate_Sell = None   
        self.Buy_at_fear = None
        self.Sell_at_greed = None
        self.Retry_times = None
        self.Retry_delay = None
        self.Polling_delay = None

    def __str__(self):
        str = 'cfg.json loaded\n\tVersion: {}\n\tRun on test net: {}\n\t'.format(self.version, self.Test_net)
        str += 'Base coin: {}\n\tQuote coin: {}\n\t'.format(self.Base, self.Quote)
        str += 'Duration_days: {}\n\tDaily_invest: {} quotes\n\t'.format(self.Duration_days, self.Daily_invest)
        str += 'Accumulate_Buy: {}\n\tAccumulate_Sell: {}\n\t'.format(self.Accumulate_Buy, self.Accumulate_Sell)
        str += 'Buy at fear lower than: {}\n\tSell at greed higher than : {}\n\t'.format(self.Buy_at_fear, self.Sell_at_greed)
        str += 'Retry_times: {}\n\tRetry_delay: {} s\n\tPolling_delay: {} s'.format(self.Retry_times, self.Retry_delay, self.Polling_delay)
        return str
    
    def new_cfg(self):
        with open('cfg.json', 'w') as file:
            json.dump(self.cfg_init, file, indent = 4)

    def load_cfg(self):
        with open('cfg.json', 'r') as file:
            self.cfg = json.load(file)
        try:
            self.version = self.cfg['Version']
            if self.version != Version:
                return False
                
            self.Test_net = self.cfg['Run_on_testnet']
            self.Base = self.cfg['Base']
            self.Quote = self.cfg['Quote']
            self.Duration_days = abs(self.cfg['Duration_days'])
            self.Daily_invest = abs(self.cfg['Daily_invest'])
            self.Accumulate_Buy = self.cfg['Accumulate_Buy']
            self.Accumulate_Sell = self.cfg['Accumulate_Sell']
            self.Buy_at_fear = abs(self.cfg['Buy_at_fear'])
            self.Sell_at_greed = abs(self.cfg['Sell_at_greed'])
            self.Retry_times = abs(self.cfg['Retry_times'])
            self.Retry_delay = abs(self.cfg['Retry_delay'])
            self.Polling_delay = abs(self.cfg['Polling_delay'])

            return True
        
        except KeyError:
            self.archive_cfg('cfg.json corrupted, old one archive as cfg_{}.json'.format(timestamp_format(os.path.getctime('cfg.json'), '%Y%m%d-%H;%M;%S')))

   
    def update_version(self):
        self.version = Version
        self.cfg['Version'] = self.version
        with open('cfg.json', 'w') as file:
            json.dump(self.cfg, file, indent = 4)
    
    def upgrade_cfg(self):
        System_Msg('cfg.json upgraded, old one archive as cfg_{}.json'.format(timestamp_format(os.path.getctime('cfg.json'), '%Y%m%d-%H;%M;%S')))
        if not os.path.isdir('archive'):
            os.mkdir('archive')
        os.rename('cfg.json', 'archive/cfg_{}.json'.format(timestamp_format(os.path.getctime('cfg.json'), '%Y%m%d-%H;%M;%S')))

        for i in self.cfg_init:
            if not i in self.cfg:
                self.cfg[i] = self.cfg_init[i]

        self.update_version()

    def archive_cfg(self, msg):
        System_Msg(msg)
        if not os.path.isdir('archive'):
            os.mkdir('archive')
        os.rename('cfg.json', 'archive/cfg_{}.json'.format(timestamp_format(os.path.getctime('cfg.json'), '%Y%m%d-%H;%M;%S')))
        self.new_cfg()
        log.log_and_show('Generate new cfg.json')
        os.system('pause')
        os._exit(0)

class Status_data:
    def __init__(self, dir) -> None:
        if not os.path.isdir(dir):
            os.mkdir(dir)
        
        self.dir = dir
        
        self.__var_init__()
        ################### TODO ################################
    
    def __var_init__(self):
        self.start_time = int(time())
        self.next_time = self.start_time
        self.exe_time = 0
        self.base_balance = 0
        self.quote_balance = 0
        self.accumulation_Buy_quote = 0
        self.accumulation_Sell_quote = 0

        self.bought_base = 0
        self.bought_quote = 0
        self.sold_base = 0
        self.sold_quote = 0

        self.operated_base = 0
        self.operated_quote = 0
        self.avg_price = 0
    
    def __str__(self):
        str = 'start_time : {}\n'.format(self.start_time)
        str += 'next_time : {}\n'.format(self.next_time)
        str += 'exe_time : {}\n'.format(self.exe_time)
        str += 'base_balance : {}\n'.format(self.base_balance)
        str += 'quote_balance : {}\n'.format(self.quote_balance)
        str += 'accumulation_Buy_quote : {}\n'.format(self.accumulation_Buy_quote)
        str += 'accumulation_Sell_quote : {}\n'.format(self.accumulation_Sell_quote)
        str += 'bought_base : {}\n'.format(self.bought_base)
        str += 'bought_quote : {}\n'.format(self.bought_quote)
        str += 'sold_base : {}\n'.format(self.sold_base)
        str += 'sold_quote : {}\n'.format(self.sold_quote)
        str += 'operated_base : {}\n'.format(self.operated_base)
        str += 'operated_quote : {}\n'.format(self.operated_quote)
        str += 'avg_price : {}\n'.format(self.avg_price)
        return str

    def load(self):
        if not os.path.isfile('{}/status.json'.format(self.dir)):
            return

        with open('{}/status.json'.format(self.dir), 'r') as file:
            temp = json.load(file)
        try: 
            self.start_time = temp['start_time']
            self.next_time = temp['next_time']
            self.exe_time = temp['exe_time']
            self.base_balance = temp['base_balance']
            self.quote_balance = temp['quote_balance']
            self.accumulation_Buy_quote = temp['accumulation_Buy_quote']
            self.accumulation_Sell_quote = temp['accumulation_Sell_quote']
            self.bought_base = temp['bought_base']
            self.bought_quote = temp['bought_quote']
            self.sold_base = temp['sold_base']
            self.sold_quote = temp['sold_quote']
            self.operated_base = temp['operated_base']
            self.operated_quote = temp['operated_quote']
            self.avg_price = temp['avg_price']
        except KeyError:
            self.__var_init__()

        del temp        
        
    def write(self):
        temp = {
            'start_time' : self.start_time,
            'next_time' : self.next_time,
            'exe_time' : self.exe_time,
            'base_balance' :  self.base_balance,
            'quote_balance' :  self.quote_balance,
            'accumulation_Buy_quote' :  self.accumulation_Buy_quote,
            'accumulation_Sell_quote' :  self.accumulation_Sell_quote,
            'bought_base' :  self.bought_base,
            'bought_quote' :  self.bought_quote,
            'sold_base' :  self.sold_base,
            'sold_quote' :  self.sold_quote,
            'operated_base' :  self.operated_base,
            'operated_quote' :  self.operated_quote,
            'avg_price' :  self.avg_price
        }        
        with open('{}/status.json'.format(self.dir), 'w') as file:
            json.dump(temp, file, indent = 4)

        del temp
    
    def archive(self):
        if os.path.isdir(self.dir) and os.path.isfile('{}/status.json'.format(self.dir)):
            if not os.path.isdir('archive'):
                os.mkdir('archive')
            copytree(self.dir, 'archive/{}_{}'.format(self.dir, timestamp_format(os.path.getctime('{}/status.json'.format(self.dir)), '%Y%m%d-%H%M%S')))
            rmtree(self.dir)
            os.mkdir(self.dir)

class Ledger:
    def __init__(self, dir, filename) -> None:
        self.file = '{}/{}.csv'.format(dir, filename)
        self.csv_head = False
        
    def set_header(self, arr = []):
        self.csv_head = arr

        if not os.path.isfile(self.file):
            with open(self.file, 'w', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(self.csv_head)

    def write(self, row = []):
        with open(self.file, 'a', newline='') as file:
            writer = csv.writer(file)
            writer.writerow(row)
        
class Open:
    def __init__(self, symbol, side) -> None:
        self.symbol = symbol
        self.side = side
        self.quote_qty = 0
        self.orderId = ''
        self.status = ''
        self.actual_base_qty = 0
        self.actual_quote_qty = 0
        self.actual_price = 0
        self.time = 0
    
    def __str__(self):
        str = 'symbol : {}\n'.format(self.symbol)
        str += 'side : {}\n'.format(self.side)
        str += 'quote_qty : {}\n'.format(self.quote_qty)
        str += 'orderId : {}\n'.format(self.side)
        str += 'actual_base_qty : {}\n'.format(self.actual_base_qty)
        str += 'actual_quote_qty : {}\n'.format(self.actual_quote_qty)
        str += 'actual_price : {}\n'.format(self.actual_price)
        str += 'time : {}'.format(self.time)
        return str

def Error_Msg(str = ''):
    log.log(str)
    str = str.split('\n')

    for i in str:
        os.system('echo [31m{} : {}'.format(datetime.now().strftime('%H:%M:%S'), i))        
    os.system('echo [0m{} :'.format(datetime.now().strftime('%H:%M:%S')))

def System_Msg(str = ''):
    log.log(str)
    str = str.split('\n')

    for i in str:
        os.system('echo [33m{} : {}'.format(datetime.now().strftime('%H:%M:%S'), i))
    os.system('echo [0m{} :'.format(datetime.now().strftime('%H:%M:%S')))

def Print_and_pause(str = ''):
    print(str)
    os.system('pause')

def precision_trim(num, digi):
    num = (int)(num * pow(10, digi))
    return num / pow(10, digi)

def timestamp_format(stamp, format = '%Y/%m/%d %H:%M:%S'):
    return strftime(format, localtime(stamp))

def argv_check():
    if len(sys.argv) < 3:
        log.show('Execution cmd :')
        log.show('main.exe <api key> <api secret> <-R : restar record>')
        os.system('pause')
        os._exit(0)

    else:
        #with other cmd
        for i in sys.argv[3:]:
            if not i.startswith('-'):
                sys.argv.pop(sys.argv.index(i))

        cmd = set(sys.argv[3:])

        for i in cmd:
            match i:
                case '-R':
                    sta.archive()
                case _:
                    pass

if __name__ == '__main__':
    delay = delay_anima()
    cfg = CFG(Version)
    sta = Status_data('status')
    ledger = Ledger('status', 'ledger')
    fng = crypto_fear_and_greed_alternative()
    argv_check()
    Symbol = {}
    Balance = {}
    Fng = {}

    try:
        ##############################################################################################################################
        ### Load Cfg File

        if not os.path.isfile('cfg.json'):
            System_Msg('cfg.json file missing. Generate a new one')
            cfg.new_cfg()
            os.system('pause')

        if not cfg.load_cfg():
            if (float)(cfg.version.split('.')[0]) != (float)(Version.split('.')[0]) or \
               (float)(cfg.version.split('.')[1]) != (float)(Version.split('.')[1]):
                # Main version different
                cfg.upgrade_cfg()
                log.show('Upgrade cfg.json, please check new config or press any key to continue')
                os.system('pause')
                cfg.load_cfg()

            elif (float)(cfg.version.split('.')[2]) < (float)(Version.split('.')[2]):
                #Sub version different
                cfg.update_version()
                cfg.load_cfg()
        
        if cfg.Buy_at_fear >= cfg.Sell_at_greed or cfg.Buy_at_fear > 100 or cfg.Sell_at_greed > 100:
            raise Exception('Config parameter Error!!\nBuy_at_fear or Sell_at_greed value error.')           

        if cfg.Retry_times < 10:
            cfg.Retry_times = 10

        if cfg.Retry_delay < 0.1:
            cfg.Retry_delay = 0.1

        log.log(str(cfg))

        ##############################################################################################################################
        ### Load status data
        sta.load()
        sta.operated_base = sta.bought_base - sta.sold_base
        sta.operated_quote = (cfg.Duration_days * cfg.Daily_invest) - sta.bought_quote

        ##############################################################################################################################
        ### Set csv head
        header = [
            'exe_time',
            '{}_balance'.format(cfg.Base),
            '{}_balance'.format(cfg.Quote),
            'trade_time',
            'trade_{}'.format(cfg.Base),
            'trade_{}'.format(cfg.Quote),
            'trade_price',
            'average_price',
            'bought_{}'.format(cfg.Base),
            'bought_{}'.format(cfg.Quote),
            'sold_{}'.format(cfg.Base),
            'sold_{}'.format(cfg.Quote),
            'F&G',
            'next_time',
            'accum_Buy',
            'accum_Sell',
            'free_{}_balance'.format(cfg.Base),
            'free_{}_balance'.format(cfg.Quote),
        ]
        ledger.set_header(header)
        del header

        ##############################################################################################################################
        ### Create client
        if cfg.Test_net:
            log.log('Run on Test Net !!!')
            client = Client_Spot(test_net = True, api_key = sys.argv[1], api_secret = sys.argv[2], url = 'https://testnet.binance.vision')
        else:
            log.log('Run on Main Net !!!')
            client = Client_Spot(test_net = False, api_key = sys.argv[1], api_secret = sys.argv[2])

    except Exception as Err:
        Err = str(Err)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        log.show('')
        Error_Msg(Err)
        log.log('Exception type: {}, in: <{}>, line: {}'.format(exc_type, fname, exc_tb.tb_lineno))
        os.system('pause')
        os._exit(0)
    
    while True:
        try:
            ### check time and run
            sta.exe_time = int(time())
            if sta.exe_time >= sta.next_time:
                rt = log.get_run_time(sta.start_time)
                separator = '=' * (2 * len(rt))
                log.log_and_show(separator + '\n' + rt)
                del rt
                del separator
                if sta.exe_time - sta.next_time > 86400:
                    #First round or pause longer than one days
                    sta.next_time = 86400 + sta.exe_time
                else:
                    sta.next_time += 86400
                sta.write()
            else:
                collect()
                delay.anima_runtime(cfg.Polling_delay, sta.start_time)
                continue

            ### Query symbol data
            retry = cfg.Retry_times
            while retry:
                temp = client.query_symbol(base = cfg.Base, quote = cfg.Quote)
                if temp == False:
                    # Query fail use old data
                    retry -= 1
                    delay.delay(cfg.Retry_delay)
                    continue
                else:
                    break
            
            if retry == 0:
                # Query symbol fail use old data if any
                log.log('Query {}{} symbol data fail {} times!!'.format(cfg.Base, cfg.Quote, cfg.Retry_times))
                if not Symbol:
                    #There's not old data
                    System_Msg('Missing symbol data, skip today')
                    del temp
                    continue
            else:
                Symbol = temp             
                log.log('Query {}{} symbol data successfully, retry {} times!!'.format(cfg.Base, cfg.Quote, cfg.Retry_times - retry))
            del temp

            ### Check cfg parameter
            if cfg.Daily_invest < float(Symbol['filters'][3]['minNotional']):
                raise Exception('Config parameter Error!!\nDaily_invest lower than minimum trade amount.')           

            ### Query wallet balance
            retry = cfg.Retry_times
            while retry:
                Balance = client.query_balance(coin = [cfg.Base, cfg.Quote])
                if Balance == False:
                    retry -= 1
                    delay.delay(cfg.Retry_delay)
                    continue
                else:
                    break
            
            if retry == 0:
                # Query balance fail skip today
                log.log('Query {}, {} Balance fail {} times!!'.format(cfg.Base, cfg.Quote, cfg.Retry_times))
                System_Msg('Fail query wallwt balance, skip today')
                del Balance
                continue
            else:
                log.log('Query {}, {} Balance successfully, retry {} times!!'.format(cfg.Base, cfg.Quote, cfg.Retry_times - retry))


            ### Query fear and greed
            retry = cfg.Retry_times
            while retry:
                Fng = fng.get_fng_today()
                if Fng == False:
                    retry -= 1
                    delay.delay(cfg.Retry_delay)
                    continue
                else:
                    break
                
            if retry == 0:
                # Query fear and greed indax fail skip today
                log.log('Query today''s fear and greed index fail {} times!!'.format(cfg.Base, cfg.Quote, cfg.Retry_times))
                System_Msg('Missing fng data, skip today')
                del Fng
                continue
            else:
                Fng['value'] = int(Fng['value'])

            ### Query Last Price
            retry = cfg.Retry_times
            while retry:
                Last_price = client.get_last_price(cfg.Base + cfg.Quote)
                if Last_price == False:
                    retry -= 1
                    delay.delay(cfg.Retry_delay)
                    continue
                else:
                    break

            if retry == 0:
                # Query last price fail
                log.log('Query {}, {} Balance fail {} times!!'.format(cfg.Base, cfg.Quote, cfg.Retry_times))
                System_Msg('Fail query {} last price, skip today'.format(cfg.Base + cfg.Quote))
                del Last_price
                continue
            else:
                log.log('Query {} last price successfully, retry {} times!!'.format(cfg.Base + cfg.Quote, cfg.Retry_times - retry))


            ### Show status
            sta.base_balance = float(Balance[cfg.Base]['free']) + float(Balance[cfg.Base]['locked'])
            sta.quote_balance = float(Balance[cfg.Quote]['free']) + float(Balance[cfg.Quote]['locked'])
            str = '{} Fear and Greed index : {} >>> {}\n'.format(datetime.now().strftime('%Y/%m/%d'), Fng['value'], Fng['value_classification'])
            str += '{} last price : {} {}'.format(cfg.Base + cfg.Quote, Last_price, cfg.Quote)
            log.log_and_show(str)
            del str

            ### Check and Do trade
            if Fng['value'] <= cfg.Buy_at_fear:
                # Buy
                if Balance[cfg.Quote]['free'] >= sta.accumulation_Buy_quote + cfg.Daily_invest and sta.operated_quote > 0:
                    # Free balance larger than daily invest value
                    order = Open(cfg.Base + cfg.Quote, 'Buy')
                    sta.accumulation_Buy_quote += cfg.Daily_invest
                    order.quote_qty = precision_trim(sta.accumulation_Buy_quote, Symbol['quoteCommissionPrecision'])

                    ## Place matket order
                    retry = cfg.Retry_times
                    while retry:
                        order.orderId = client.place_market_order_quote(order.symbol, order.side, order.quote_qty)
                        if order.orderId == False:
                            retry -= 1
                            delay.delay(cfg.Retry_delay)
                            continue
                        else:
                            break

                    if retry == 0:
                        # Open order fail
                        log.log('Open {} {} {} order fail {} times!!'.format(order.quote_qty, order.symbol, order.side, cfg.Retry_times))
                        System_Msg('Fail open order, skip today')
                        del order
                        continue
                    else:
                        # take order ID
                        log.log_and_show('{} {} order creat success!'.format(order.symbol, order.side))

                    ## Check order status
                    retry = cfg.Retry_times
                    while retry:
                        order.status = client.get_order_status(order.symbol, order.orderId)
                        if order.status != False:
                            match order.status['status']:
                                case 'FILLED':
                                    log.log('{} {} order execute filled, query: {} times'.format(order.symbol, order.side, cfg.Retry_times - retry))
                                    break
                                case 'REJECTED' | 'CANCELED' | 'EXPIRED' | 'PENDING_CANCEL':
                                    retry = 'F'
                                    break
                                case 'NEW' | 'PARTIALLY_FILLED':
                                    delay.delay(2)
                                    pass
                                case _:
                                    delay.delay(2)
                                    pass
                            retry -= 1
                            delay.delay(cfg.Retry_delay)
                            continue
                        else:
                            break
                    if retry == 0:
                        # retry fail
                        System_Msg('Query {} {} order status Fail!!, query: {} times, order_status: {}'.format(order.symbol, order.side, cfg.Retry_times - retry, order.status))
                    elif retry == 'F':
                        # order execute fail
                        System_Msg('{} {} order execute Fail!!, query: {} times, order_status: {}'.format(order.symbol, order.side, cfg.Retry_times - retry, order.status))
                        del order
                        continue
                    del retry

                    try:
                        order.actual_quote_qty = float(order.status['cummulativeQuoteQty'])
                        order.actual_base_qty = float(order.status['executedQty'])
                        order.actual_price = order.actual_quote_qty / order.actual_base_qty
                        order.time = float(order.status['time']) / 1000
                    except NameError:
                        order.actual_quote_qty = order.quote_qty
                        order.actual_base_qty = order.quote_qty / Last_price
                        order.actual_price = Last_price
                        order.time = float(time())
                    
                    #average
                    sta.avg_price = ((sta.operated_base * sta.avg_price) + order.actual_quote_qty) / (sta.operated_base + order.actual_base_qty)
                    sta.bought_base += order.actual_base_qty
                    sta.bought_quote += order.actual_quote_qty

                    if cfg.Accumulate_Buy:
                        sta.accumulation_Buy_quote -= order.actual_quote_qty
                        if sta.accumulation_Buy_quote < 0:
                            sta.accumulation_Buy_quote = 0
                    else:
                        sta.accumulation_Buy_quote = 0
                    
                    str = '{} Buy {:.5f} {} at {:.2f} {} ({:.2f} {}) Successfully!!'.format(datetime.now().strftime('%Y/%m/%d'),
                                                                                        order.actual_base_qty,
                                                                                        cfg.Base,
                                                                                        order.actual_price,
                                                                                        cfg.Quote,
                                                                                        order.actual_quote_qty,
                                                                                        cfg.Quote)
                    log.log_and_show(str)
                    del str
                elif sta.operated_quote <= 0:
                    log.log_and_show('Fear and greed {} DCA for {} days COMPLETE!!'.format(cfg.Quote + cfg.Base, cfg.Duration_days))
                    os.system('pause')
                    os._exit(0)
                else:
                    log.log_and_show('Free {} balance lower than Daily invest volue!\nPause buy {} today!'.format(cfg.Quote, cfg.Base))
                    if cfg.Accumulate_Buy:
                        sta.accumulation_Buy_quote += cfg.Daily_invest

            else:
                if cfg.Accumulate_Buy:
                    sta.accumulation_Buy_quote += cfg.Daily_invest

            ### Summary
            sta.operated_base = sta.bought_base - sta.sold_base
            sta.operated_quote = (cfg.Duration_days * cfg.Daily_invest) - sta.bought_quote

            separator = '---------------------------------------------\n'
            str = separator
            str += 'BUY : \n\t{}\t:\t{:.5f}\n\t{}\t:\t{:.2f}\n'.format(cfg.Base, sta.bought_base, cfg.Quote, sta.bought_quote)
            str += separator
            str += 'SELL : \n\t{}\t:\t{:.5f}\n\t{}\t:\t{:.2f}\n'.format(cfg.Base, sta.sold_base, cfg.Quote, sta.sold_quote)
            str += separator
            str += 'Balance : \n\t{}\t:\t{:.5f}\n\t{}\t:\t{:.2f}\n'.format(cfg.Base, sta.operated_base, cfg.Quote, sta.operated_quote)
            str += separator
            str += 'Average price : {:.2f} {}\n'.format(sta.avg_price, cfg.Quote)
            str += separator.split('\n')[0]

            log.log_and_show(str)
            del str
            del separator

            ### Record csv and sta
            try:
                row = [
                    '[{}]'.format(timestamp_format(sta.exe_time)),      # exe_time
                    sta.operated_base,                                  # base_balance
                    sta.operated_quote,                                 # quote_balance
                    '[{}]'.format(timestamp_format(order.time)),        # trade_time
                    order.actual_base_qty,                              # trade_{}
                    order.actual_quote_qty,                             # trade_{}
                    order.actual_price,                                 # trade_price
                    sta.avg_price,                                      # average_price
                    sta.bought_base,                                    # bought_{}
                    sta.bought_quote,                                   # bought_{}
                    sta.sold_base,                                      # sold_{}
                    sta.sold_quote,                                     # sold_{}
                    Fng['value'],                                       # F&G
                    '[{}]'.format(timestamp_format(sta.next_time)),     # next_time
                    sta.accumulation_Buy_quote,                         # accum_Buy
                    sta.accumulation_Sell_quote,                        # accum_Sell
                    Balance[cfg.Base]['free'],                          # free_{}_balance
                    Balance[cfg.Quote]['free'],                         # free_{}_balance
                ]
                ledger.write(row)
                del row
                del order
            except NameError:
                row = [
                    '[{}]'.format(timestamp_format(sta.exe_time)),      # exe_time
                    sta.operated_base,                                  # base_balance
                    sta.operated_quote,                                 # quote_balance
                    '--',                                               # trade_time
                    '--',                                               # trade_{}
                    '--',                                               # trade_{}
                    '--',                                               # trade_price
                    sta.avg_price,                                      # average_price
                    sta.bought_base,                                    # bought_{}
                    sta.bought_quote,                                   # bought_{}
                    sta.sold_base,                                      # sold_{}
                    sta.sold_quote,                                     # sold_{}
                    Fng['value'],                                       # F&G
                    '[{}]'.format(timestamp_format(sta.next_time)),     # next_time
                    sta.accumulation_Buy_quote,                         # accum_Buy
                    sta.accumulation_Sell_quote,                        # accum_Sell
                    Balance[cfg.Base]['free'],                          # free_{}_balance
                    Balance[cfg.Quote]['free'],                         # free_{}_balance
                ]
                ledger.write(row)
                del row
            
            del Fng
            del Balance
            del Last_price
            sta.write()
            log.log('Next time buy if fear\t: {:.2f}\t{}\nNext time sell if greed\t: {:.2f}\t{}'.format(
                                                                                sta.accumulation_Buy_quote + cfg.Daily_invest,
                                                                                cfg.Quote,
                                                                                sta.accumulation_Sell_quote + cfg.Daily_invest,
                                                                                cfg.Quote))
           
        except Exception as Err:
            Err = str(Err)
            exc_type, exc_obj, exc_tb = sys.exc_info()
            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
            log.show('')

            match Err:
                case "('Connection aborted.', RemoteDisconnected('Remote end closed connection without response'))":
                    System_Msg(Err)
                    log.log('Exception type: {}, in: <{}>, line: {}'.format(exc_type, fname, exc_tb.tb_lineno))
                    delay.anima_runtime(cfg.Polling_delay, sta.start_time)
                    continue
                case _:
                    Error_Msg(Err)
                    log.log('Exception type: {}, in: <{}>, line: {}'.format(exc_type, fname, exc_tb.tb_lineno))
                    os.system('pause')
                    os._exit(0)





