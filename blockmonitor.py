#/usr/bin/python
# -*- coding: UTF-8 -*-

import datetime
import threading
import time
import requests
import json
import pytz
from config import Config  
from logger import Logger
from text  import Text
from votemgr import VoteMgr

class BlockInfo(object):
    def __init__(self):
         self.trxs = []

    def addTrx(self,trx):
         self.trxs.append(trx)

class Transaction(object):
    def __init__(self):
         self.trx_id = 0
         self.actions= []

    def addAction(self,action):
         self.actions.append(action)

class Action(object):
    def __init__(self,account,name,data):
         self.account = account 
         self.name    = name
         self.data    = data

class Voter(object):
    def __init__(self,owner,proxy,producers,stake,is_proxy):
       self.owner = owner
       self.proxy = proxy
       self.producers = producers
       self.stake = stake
       self.is_proxy = is_proxy

class BlockMgr(object):

    __instance = None

    def __init__(self):
       pass
     
    def __new__(cls, *args, **kwargs):
       if not BlockMgr.__instance:
           BlockMgr.__instance = object.__new__(cls,*args, **kwargs)
       return BlockMgr.__instance

    def Instance(self):
        return BlockMgr.__instance

    def threadFun(self,arg):

       while(True):
            
            voters = self.requestVoters(self.sartAccount)
            time.sleep(1)


    def Start(self):

         self.sartAccount = ""
              
         t =threading.Thread(target=self.threadFun,args=(1,))
         t.setDaemon(True)#设置线程为后台线程
         t.start()
   

    def requestVoters(self,start):

        headers = {'content-type': "application/json"}
        url = Config.HTTP_URL + "get_table_rows"
        try:
             start = ' "{0}"'.format(start)
             r = requests.post(url,data =json.dumps({"scope":"eosio","code":"eosio","table":"producers","json":true,"limit":3,"lower_bound":start}),headers = headers);
             print r.text
             if( r.status_code == 200):
                 js = json.loads(r.text)

                 if((not js is None) and (not js["rows"] is None)):
                      for row in js["rows"]:
                         owner = row["owner"]
                         total_votes = row["total_votes"]
                         self.sartAccount = owner
                         print owner,total_votes
 
                 if( (not js is None) and (js["more"] == 0) ):
                         self.sartAccount = ""                        
                    
             else:
                 print "request error1"
                 self.sartAccount = ""
        except:
             print "request error2"
             self.sartAccount = "" 

      
