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
Version = '0.0.00'
Date = '2021/12/24'

##############################################################################################################################
### init log
log = Log('log')
log.log('\n=============================START==============================')
log.log_and_show('Bybit Fear and Greed index DCA trading bot ver {} {}'.format(Version, Date))

class CFG:
    def __init__(self, version) -> None:
        self.version = version
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
        
        self.cfg_init = {
                            'Version' : version,
                            'Run_on_testnet' : True,
                            'Base' : 'BTC',
                            'Quote' : 'USDT',
                            'Duration_days' : 365,
                            'Daily_invest' : 0,
                            'Accumulate_Buy' : True,
                            'Accumulate_Sell' : False,
                            'Buy_at_fear' : 25,
                            'Sell_at_greed' : 75,
                            'Retry_times' : 30,
                            'Retry_delay' : 0.2,
                            'Polling_delay' : 600
                        }
    
        self.symbol = None

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

    def log_cfg(self):
        str = 'cfg.json loaded\n\tVersion: {}\n\tRun on test net: {}\n\t'.format(self.version, self.Test_net)
        str += 'Base coin: {}\n\tQuote coin: {}\n\t'.format(self.Base, self.Quote)
        str += 'Duration_days: {}\n\tDaily_invest: {} quotes\n\t'.format(self.Duration_days, self.Daily_invest)
        str += 'Accumulate_Buy: {}\n\Accumulate_Sell: {}\n\t'.format(self.Accumulate_Buy, self.Accumulate_Sell)
        str += 'Buy at fear lower than: {}\n\tSell at greed higher than : {}\n\t'.format(self.Buy_at_fear, self.Sell_at_greed)
        str += 'Retry_times: {}\n\tRetry_delay: {} s\n\tPolling_delay: {} s'.format(self.Retry_times, self.Retry_delay, self.Polling_delay)
        log.log(str)
        del str
    
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
        
        if not os.path.isfile('{}/status.json'.format(dir)):
            with open('{}/status.json'.format(dir), 'w') as file:
                pass
            del file

        self.start_time = int(time())
        self.next_time = 0
        self.exe_time = 0
        self.base_balance = 0
        self.quote_balance = 0
        self.accumulation_Buy_quote = 0
        self.accumulation_Sell_quote = 0

        self.dir = dir

        self.csv_head = ['time', 'balance']
        ################### TODO ################################
    
    def __str__(self):
        str = 'start_time : {}\n'.format(self.start_time)
        str += 'next_time : {}\n'.format(self.next_time)
        str += 'exe_time : {}\n'.format(self.exe_time)
        str += 'base_balance : {}\n'.format(self.base_balance)
        str += 'quote_balance : {}\n'.format(self.quote_balance)
        str += 'accumulation_Buy_quote : {}\n'.format(self.accumulation_Buy_quote)
        str += 'accumulation_Sell_quote : {}\n'.format(self.accumulation_Sell_quote)
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
        except KeyError:
            self.start_time = int(time())
            self.next_time = 0
            self.exe_time = 0
            self.base_balance = 0
            self.quote_balance = 0
            self.accumulation_Buy_quote = 0
            self.accumulation_Sell_quote = 0

        del temp        
        
    def write_status(self):
        temp = {
            'start_time' : self.start_time,
            'next_time' : self.next_time,
            'exe_time' : self.exe_time,
            'base_balance' :  self.base_balance,
            'quote_balance' :  self.quote_balance,
            'accumulation_Buy_quote' :  self.accumulation_Buy_quote,
            'accumulation_Sell_quote' :  self.accumulation_Sell_quote
        }        
        with open('{}/status.json'.format(self.dir), 'w') as file:
            json.dump(temp, file, indent = 4)

        del temp
    
    def record_balance(self):
        if not os.path.isfile('{}/balance.csv'.format(self.dir)):
            with open('{}/balance.csv'.format(self.dir), 'a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow(self.csv_head)
        
        with open('{}/balance.csv'.format(self.dir), 'a', newline='') as file:
            writer = csv.writer(file)
            # writer.writerow([ , ])
    
    def archive(self):
        if os.path.isdir(self.dir):
            if not os.path.isdir('archive'):
                os.mkdir('archive')
            copytree(self.dir, 'archive/{}_{}'.format(self.dir, timestamp_format(os.path.getctime('{}/status.json'.format(self.dir)), '%Y%m%d-%H%M%S')))
            rmtree(self.dir)
            os.mkdir(self.dir)
        
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

def qty_trim(qty, step):
    digi = abs((int)(format(step, '1E').split('E')[1]))
    qty = (int)(qty * pow(10, digi))
    step = (int)(step * pow(10, digi))
    qty -= qty % step    
    return qty / pow(10, digi)

def price_trim(price, tick):
    digi = abs((int)(format(tick, '1E').split('E')[1]))
    price = (int)(price * pow(10, digi))
    tick = (int)(tick * pow(10, digi))
    
    price -= price % tick    
    return price / pow(10, digi)

def timestamp_format(stamp, format = '%H:%M:%S %Y-%m-%d'):
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

        cfg.log_cfg()

        ##############################################################################################################################
        ### Load status data
        sta.load()

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
            if int(time()) >= sta.next_time:
                log.log_and_show(log.get_run_time(sta.start_time))
                if sta.next_time == 0 or int(time()) - sta.next_time > 86400:
                    #First round or pause longer than one days
                    sta.next_time = 86400 + int(time())
                else:
                    sta.next_time += 86400
                sta.write_status()
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
                del Balance
                continue
            else:
                log.log('Query {} last price successfully, retry {} times!!'.format(cfg.Base + cfg.Quote, cfg.Retry_times - retry))


            ### Show status
            display_str = '{} Fear and Greed index : {} >>> {}\n'.format(datetime.now().strftime('%Y/%m/%d'), Fng['value'], Fng['value_classification'])
            display_str += 'Wallet Balance : \n\t{}\t:\t{:.5f}\n\t{}\t:\t{:.2f}\n'.format(cfg.Base, Balance[cfg.Base]['free'], cfg.Quote, Balance[cfg.Quote]['free'])
            display_str += '{} last price : {} {}'.format(cfg.Base + cfg.Quote, Last_price, cfg.Quote)
            log.log_and_show(display_str)
            del display_str

            ### Check and Do trade
            if Fng['value'] <= cfg.Buy_at_fear:
                # Buy
                if Balance[cfg.Quote]['free'] >= sta.accumulation_Buy_quote + cfg.Daily_invest:
                    # Free balance larger than daily invest value
                    order = Open(cfg.Base + cfg.Quote, 'Buy')
                    # order.quote_qty = qty_trim(sta.accumulation_Buy_quote + cfg.Daily_invest, Symbol['quotePrecision'])
                    order.quote_qty = sta.accumulation_Buy_quote + cfg.Daily_invest

                    ## Place matket order
                    retry = cfg.Retry_times
                    while retry:
                        order.orderId = client.place_market_order(order.symbol, order.side, order.quote_qty)
                        if order.orderId == False:
                            retry -= 1
                            delay.delay(cfg.Retry_delay)
                            continue
                        else:
                            break

                    if retry == 0:
                        # Open order fail
                        log.log('Open {} {} order fail {} times!!'.format(order.symbol, order.side, cfg.Quote, cfg.Retry_times))
                        System_Msg('Fail open {} {}, skip today'.format(order.symbol, order.side))
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
                                    delay.delay(5)
                                    pass
                                case _:
                                    pass
                            retry -= 1
                            delay.delay(cfg.Retry_delay)
                            continue
                        else:
                            break
                    if retry == 0 or retry == 'F':
                        # retry fail
                        Error_Msg('{} {} order created Fail!!, query: {} times, order_status: {}'.format(order.symbol, order.side, cfg.Retry_times - retry, order.status))
                        del order
                        continue                                 
                    del retry

                    log.log_and_show('{} {} about {:.2f} {} {} Successfully!!'.format(datetime.now().strftime('%Y/%m/%d'), order.side, cfg.Daily_invest, cfg.Quote, cfg.Base))
                    order.actual_quote_qty = float(order.status['cummulativeQuoteQty'])
                    order.actual_base_qty = float(order.status['executedQty'])
                    order.actual_price = order.actual_quote_qty / order.actual_base_qty
                    order.time = order.status['time']

                    sta.accumulation_Buy_quote = 0
                else:
                    log.log_and_show('Free {} balance lower than Daily invest volue!\nPause buy {} today!'.format(cfg.Quote, cfg.Base))
            
            else:
                sta.accumulation_Buy_quote += cfg.Daily_invest

            ##Sell at greed function not ready

            ### Record csv ans sta
            # TODO
            # TODO
            # TODO

           
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





