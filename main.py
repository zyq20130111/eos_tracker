# -*- coding: utf-8 -*-
# filename: main.py
import threading
import time

from blockmonitor import BlockMgr
from logger import Logger
from votemgr import VoteMgr
import sys

urls = (
    '/wx', 'Handle',
)


if __name__ == '__main__':

    Logger().Init()
    #BlockMgr().Instance().Start()
    VoteMgr().Instance().regProducer("accountnum11",1)
    VoteMgr().Instance().regProducer("accountnum22",1)
    VoteMgr().Instance().bwAction("proxyproxy11","proxyproxy11",100000,0)
    VoteMgr().Instance().bwAction("vote11111111","accountnum11",400000,0)
    VoteMgr().Instance().bwAction("vote11111122","accountnum22",600000,0) 
    VoteMgr().Instance().unbwAction("vote11111111",300000)
    VoteMgr().Instance().unbwAction("vote11111122",500000)
    VoteMgr().Instance().regProxy("proxyproxy11",1)
    VoteMgr().Instance().voteAction("vote11111111","proxyproxy11",[])   
    VoteMgr().Instance().voteAction("proxyproxy11","",['accountnum11','accountnum22'])
    VoteMgr().Instance().regProxy("proxyproxy11",0)
    VoteMgr().Instance().regProxy("proxyproxy11",1)
    print "test finish"
    try:
        while 1:
            pass
    except KeyboardInterrupt:
        pass


