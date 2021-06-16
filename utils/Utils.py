# coding=utf-8
# author=XingLong Pan
# date=2016-11-07

import time
import random


class Utils:

    @staticmethod
    def delay(min_second, max_second):
        sleepSecond=random.randrange(min_second, max_second);
        print(str(sleepSecond)+'s后继续操作...')
        time.sleep(sleepSecond)
