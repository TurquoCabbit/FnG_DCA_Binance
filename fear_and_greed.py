import requests
import time
from datetime import datetime
import os

class crypto_fear_and_greed_alternative:
    def __init__(self) -> None:
        self.endpoint = 'https://api.alternative.me/fng/'

    def get_fng_json(self):
        fng = requests.get(self.endpoint)
        if fng.status_code == 200:
            return fng.json()
        else:
            return False

    def get_fng_value(self):
        return self.get_fng_json()['data'][0]['value']

    def get_fng_classification(self):
        return self.get_fng_json()['data'][0]['value_classification']
        
    def get_fng_time(self):
        return self.get_fng_json()['data'][0]['timestamp']

    def get_fng_time_until_update(self):
        return self.get_fng_json()['data'][0]['time_until_update']

    def get_fng_today(self):
        fng = self.get_fng_json()
        if not fng:
            return False
        today_stamp = int((time.time() // 86400) * 86400)
        data_stamp = int(fng['data'][0]['timestamp'])
        if today_stamp == data_stamp:
            return fng['data'][0]
        else:
            return False


if __name__ == '__main__':
    fng = crypto_fear_and_greed_alternative()
    fng_data = fng.get_fng_today()
    if fng_data:
        print(' {}'.format(datetime.now().strftime('%Y-%m-%d')))
        print(' Today\'s fear & greed : {}, {}.'.format(fng_data['value'], fng_data['value_classification']))
    else:
        print('Get fear & greed Fail!!')
        
    print()
    os.system('pause')