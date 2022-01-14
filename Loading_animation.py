from time import sleep
from time import time

class delay_anima:
    def __init__(self) -> None:
        self.bar = ['▏', '▎', '▍', '▌', '▋', '▊', '▉', '█']
        self.cube = ['▄ ', '▀ ', ' ▀', ' ▄']
        self.interval = 0.25

    def anima_bar(self, times):
        self.cnt = (int)(times / self.interval)
        while self.cnt > 0:
            for i in self.bar:
                print('  {} '.format(i), end = '\r')
                sleep(self.interval)
                self.cnt -= 1
                if self.cnt < 1:
                    break

    def anima_cube(self, times, clockwise = False):
        self.cnt = (int)(times / self.interval)
        while self.cnt > 0:
            for i in self.cube:
                print('  {}'.format(i), end = '\r')
                sleep(self.interval)
                self.cnt -= 1
                if self.cnt < 1:
                    break

    def anima_runtime(self, times, start):
        self.cnt = (int)(times)
        while self.cnt > 0:
            self.cnt -= 1
            m, s = divmod((int)(time()) - start, 60)
            h, m = divmod(m, 60)
            d, h = divmod(h, 24)
            print('  Run time : {:d} days {:02d} h {:02d} m {:02d} s'. format((int)(d), (int)(h), (int)(m), (int)(s)), end = '\r')
            sleep(1)

    
    def delay(self, time):
        sleep(time)

    
if __name__ == '__main__':
    test = delay_anima()

    test.anima_bar(10)
    test.anima_cube(10)