from binance.spot import Spot
import binance.error
import os
from datetime import datetime
import win32api

from Make_log import Log


class Client_Spot:
    def __init__(self, test_net, api_key, api_secret, url = None, timeout = 60) -> None:
        
        if url == None:
            self.client = Spot(key = api_key, secret = api_secret, timeout = timeout)
        else:
            self.client = Spot(base_url = url, key = api_key, secret = api_secret, timeout = timeout)

        if test_net:
            self.test_net = True
        else:
            self.test_net = False
        
        self.log = Log('log', '%Y-%m')
        self.log.log('Client init : \n\tTest net : {}\n\tBase_url : {}\n\tTimeout : {} s'.format(self.test_net, url, timeout))
    
    def Error_Msg(self, str = ''):
        self.log.log(str)
        str = str.split('\n')

        for i in str:
            os.system('echo [31m{} : {}'.format(datetime.now().strftime('%H:%M:%S'), i))        
        os.system('echo [0m{} :'.format(datetime.now().strftime('%H:%M:%S')))
    
    def error_message(self, err, source = ''):
        msg = source + '\n'
        header = False
        code = False
        # print(type(err))
        match type(err):
            case binance.error.ServerError:
                code = str(err.status_code)
                msg += '\thttp_code : {}\n'.format(err.status_code)
                msg += '\terror_message : {}'.format(err.error_message)
                pass
            case binance.error.ClientError:
                if str(err.error_code) == 'None':
                    code = str(err.status_code)
                    msg += '\thttp_code : {}'.format(err.status_code)
                else:
                    code = str(err.error_code)
                    msg += '\thttp_code : {}\n'.format(err.status_code)
                    msg += '\terror_code : {}\n'.format(err.error_code)
                    msg += '\terror_message : {}'.format(err.error_message)
                header = str(err.header)
                pass
            case binance.error.ParameterRequiredError:
                msg += '\terror_message : ' + str(err)
                pass
            case binance.error.ParameterValueError:
                msg += '\terror_message : ' + str(err)
                pass
            case binance.error.ParameterTypeError:
                msg += '\terror_message : ' + str(err)
                pass
            case binance.error.ParameterArgumentError:
                msg += '\terror_message : ' + str(err)
                pass
            case _:
                # Not api error
                self.Error_Msg(msg)
                if header:
                    self.log.log('\t' + header)
                raise Exception(err)

        self.Error_Msg(msg)
        if header:
            self.log.log('\t' + header)

        return code

    def system_status(self):
        try:
            sta = self.client.system_status()
            if sta['status'] == 0:
                return True
            else:
                return sta['msg']
        except Exception as err:
            ret_code = self.error_message(err, 'Get system status Fail!!')
            match ret_code:
                case '404':
                    self.log.log('Unsupport API')
                    return False
                case _:
                    self.log.log('untrack_error_code')
                    return False

    
    def sync_time(self):
        try:
            Time = datetime.utcfromtimestamp(float(self.client.time()['serverTime'] / 1000))
        except Exception as err:
            ret_code = self.error_message(err, 'Get server time Fail!!')
            match ret_code:
                case _:
                    self.log.log('untrack_error_code')
                    return False

        year = int(Time.year)
        month = int(Time.month)
        dayOfWeek = int(Time.weekday()) 
        day = int(Time.day)
        hour = int(Time.hour)
        minute = int(Time.minute)
        second = int(Time.second)
        millseconds = int((Time.microsecond)/1000)

        try:
            win32api.SetSystemTime(year, month, dayOfWeek, day, hour, minute ,second, millseconds)
            return True
        except:
            return False

    def query_symbol(self, base = False, quote = False):
        try:
            if not base and not quote:
                # No specific symbol, return all
                return self.client.exchange_info()['symbols']
            else:
                return self.client.exchange_info(symbol = base + quote)['symbols'][0]
            
        except Exception as err:
            ret_code = self.error_message(err, 'Query symbol Fail!!')
            match ret_code:
                case _:
                    self.log.log('untrack_error_code')
                    return False
                    
    def query_balance(self, coin = ['USDT', 'BTC']):
        try:
            data = self.client.account()
            if data['accountType'] != 'SPOT':
                return False
            else:
                rc = {}
                for i in data['balances']:
                    if i['asset'] in coin:
                        rc[i['asset']] = i
                        rc[i['asset']]['free'] = float(rc[i['asset']]['free'])
                        rc[i['asset']]['locked'] = float(rc[i['asset']]['locked'])
                del data
                return rc

        except Exception as err:
            ret_code = self.error_message(err, 'Query wallet balance Fail!!')
            match ret_code:
                case _:
                    self.log.log('untrack_error_code')
                    return False

    def get_last_price(self, symbol = 'all'):
        try:
            if symbol == 'all':
                rc = {}
                for i in self.client.ticker_price():
                    rc[i['symbol']] = float(i['price'])
                return rc
            else:
                return float(self.client.ticker_price(symbol = symbol)['price'])
        except Exception as err:
            ret_code = self.error_message(err, 'Query lasted Price Fail!!')
            match ret_code:
                case '-1121':
                    return False
                case _:
                    self.log.log('untrack_error_code')
                    return False

    def get_avg_price(self, symbol = 'BTCUSDT'):
        try:
            return float(self.client.avg_price(symbol = symbol)['price'])
        except Exception as err:
            ret_code = self.error_message(err, 'Query average Price Fail!!')
            match ret_code:
                case '-1121':
                    return False
                case _:
                    self.log.log('untrack_error_code')
                    return False

    def place_market_order_quote(self, symbol, side, quote_qty):
        try:
            side = side.upper()
            if side == 'BUY' or side == 'SELL':
                return self.client.new_order(
                                                symbol = symbol,
                                                side = side,
                                                type = 'MARKET',
                                                quoteOrderQty = quote_qty,
                                            )['clientOrderId']
            else:
                return False

        except Exception as err:
            ret_code = self.error_message(err, 'Place market order Fail!!')
            match ret_code:
                case '-1121':
                    return False
                case _:
                    self.log.log('untrack_error_code')
                    return False

    def place_market_order_base(self, symbol, side, base_qty):
        try:
            side = side.upper()
            if side == 'BUY' or side == 'SELL':
                return self.client.new_order(
                                                symbol = symbol,
                                                side = side,
                                                type = 'MARKET',
                                                quantity = base_qty,
                                            )['clientOrderId']
            else:
                return False

        except Exception as err:
            ret_code = self.error_message(err, 'Place market order Fail!!')
            match ret_code:
                case '-1121':
                    return False
                case _:
                    self.log.log('untrack_error_code')
                    return False
    
    def get_order_status(self, symbol, ID):
        try:
            data = self.client.get_order(symbol = symbol, origClientOrderId = ID)
            if data['clientOrderId'] == ID:
                return data
            else:
                return False
        except Exception as err:
            ret_code = self.error_message(err, 'Get Order status Fail!!')
            match ret_code:
                case '-1121':
                    return False
                case _:
                    self.log.log('untrack_error_code')
                    return False

