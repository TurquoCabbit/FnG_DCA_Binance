from datetime import datetime
from time import time
import os

class Log:
    def __init__(self, dir = '') -> None:
        self.dir = dir
        if self.dir != '':
            if not os.path.isdir(self.dir):
                os.mkdir(self.dir)

    def show(self, str = ''):
        str = str.split('\n')
        
        for i in str:
            print('{} : {}'.format(datetime.now().strftime('%H:%M:%S'), i))
        

    def log(self, str = ''):
        str = str.split('\n')

        with open('{}/{}.log'.format(self.dir, datetime.now().strftime('%Y-%m-%d')), 'a') as file:
            for i in str:
                file.writelines('{} : {}\n'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), i))


    def log_and_show(self, str = ''):
        str = str.split('\n')
        
        with open('{}/{}.log'.format(self.dir, datetime.now().strftime('%Y-%m-%d')), 'a') as file:
            for i in str:
                print('{} : {}'.format(datetime.now().strftime('%H:%M:%S'), i))
                file.writelines('{} : {}\n'.format(datetime.now().strftime('%Y-%m-%d %H:%M:%S'), i))
    
    def get_run_time(self, start):
        m, s = divmod(time() - start, 60)
        h, m = divmod(m, 60)
        d, h = divmod(h, 24)
        return 'Run time : {:d} days {:02d} h {:02d} m {:02d} s'. format((int)(d), (int)(h), (int)(m), (int)(s))
