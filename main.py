# -*- coding: utf-8 -*-
# filename: main.py
import threading
import time

from blockmonitor import BlockMgr
from logger import Logger
import sys

urls = (
    '/wx', 'Handle',
)


if __name__ == '__main__':

    Logger().Init()
    BlockMgr().Instance().Start()

    try:
        while 1:
            pass
    except KeyboardInterrupt:
        pass


