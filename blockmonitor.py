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

           curId = self.getInfo()

           if(self.block_num_id < curId):
               
               self.block_num_id = self.block_num_id + 1
               time.sleep(0.01)
               self.getBlockInfo(self.block_num_id)

               f = open('block.txt', 'w')
               f.write(str(self.block_num_id) + " curnumid=" + str(curId))
               f.flush()

           else:
              Logger().Log("start_block_id access curnumid:{0}".format(curId))

    def Start(self):

         self.block_num_id = Config.START_BLOCK_NUM_ID
              
         t =threading.Thread(target=self.threadFun,args=(1,))
         t.setDaemon(True)#设置线程为后台线程
         t.start()

   
    def parseBlock(self,blockJson):
        
        Logger().Log(Text.TEXT27)       
        block = BlockInfo()        
        if("transactions" in blockJson):
              for trx in blockJson["transactions"]:
                  trxObj =  self.parseTransaction(trx)
                  block.addTrx(trxObj)
        else:
            Logger().Log('not exsit transaction')
        return block

    def parseTransaction(self,trxJson):

        Logger().Log(Text.TEXT28)
        trx = Transaction()
        if("trx" in trxJson):

           trxid = "00000000"
           if("id" in trxJson["trx"]):
             trxid = trxJson["trx"]["id"]
            

           if("transaction" in trxJson["trx"]):
              if("actions" in trxJson["trx"]["transaction"]):
                  for actionJson in trxJson["trx"]["transaction"]["actions"] :
                         act =  self.parseAction(actionJson,trxid)
                         if(not act is None):
                            trx.addAction(act)

        return trx       
         
    
    def getEOS(self,str):
        
        strs = str.split("EOS")
        if(len(strs) <= 0 ):
            return None
        eos  = float(strs[0])

        return eos
     
    def parseAction(self,actionJson,trxid):
        
        Logger().Log(Text.TEXT29)
        action = Action(actionJson.get("account"),actionJson.get("name"),actionJson.get("data"))
        
        if(action.data is None):
            return None

        if(action.account == "eosio" and action.name == "voteproducer"):
            
            voter = action.data.get("voter")
            proxy = action.data.get("proxy")
            producers = action.data.get("producers")

            if(produces is None):
               return None

            self.voteAction(voter,proxy,producers)                   

        elif(action.account == "eosio" and action.name == "delegatebw"):
         
            from = action.data.get("from")
            receiver = action.data.get("receiver")
            transfer = action.data.get("transfer")

            net = action.data.get("stake_net_quantity")
            net = self.getEOS(net)


            cpu = action.data.get("stake_cpu_quantity")
            cpu = self.getEOS(cpu)
          
            total =long((cpu + net) * 10000)
                           

            self.bwAction(from,receiver,total,transfer)

        elif(aciton.account == "eosio" and action.name == "undelegatebw"):
            
            voter = action.data.get("from")

            net = action.data.get("stake_net_quantity")
            net = self.getEOS(net)


            cpu = action.data.get("stake_cpu_quantity")
            cpu = self.getEOS(cpu)

            self.unbwAction(voter,total)

        elif(aciton.account == "eosio" and action.name == "regproxy"):
            proxy = action.data.get("proxy")
            isproxy = action.data.get("isproxy") 
            self.regProxy(proxy,isproxy)

        elif(action.account == "eosio" and action.name = "unregproxy"):
            proxy = action.data.get("proxy")
            isproxy = action.data.get("isproxy")
            self.regProxy(proxy,isproxy)                   

        elif(action.account == "eosio" and action.name == "regproducer"):
            producer = action.data.get("producer")
            url = action.data.get("url")        
            self.regProducer(producer,1)
    
        elif(action.account == "eosio" and action.name == "unregprod"):
            producer = action.data.get("producer")
            self.regProducer(producer,0)
        return action;

    def voteAction(voter,proxy,producers):
        VoteMgr().Instance().voteAction(voter,proxy,producers)        

    def bwAction(self,voter,total,transfer):
        VoteMgr().Instance().bwAction(voter,total,transfer)

    def unbwAction(self,voter,total):
        VoteMgr().Instance().unbwAction(voter,total)

    def regProxy(self,proxy,isproxy):
         VoteMgr().Instance().regProxy(proxy,isproxy)

    def regProducer(self,producer,active):
        VoteMgr().Instance().regProducer(producer,active)
       
    def getBlockInfo(self,blockid):
     
        print(Text.TEXT10 % (blockid))
        headers = {'content-type': "application/json"}
        url = Config.HTTP_URL + "get_block"
        try:
             r = requests.post(url,data =json.dumps({"block_num_or_id":blockid}),headers = headers);
             if( r.status_code == 200):
                 js = json.loads(r.text)
                 return self.parseBlock(js)
             else:
                 Logger().Log(Text.Text11)
                 return None
        except:
             Logger().Log(Text.TEXT11)
             return None

    def getAccount(self,account):

        Logger().Log(Text.TEXT12)
        headers = {'content-type': "application/json"}
        url = Config.HTTP_URL + "get_account"
        try:
             r = requests.post(url,data =json.dumps({"account_name":account}),headers = headers);
             if( r.status_code == 200):
                 js = json.loads(r.text)
                 return js
             else:
                 return None
        except:
             Logger().Log(Text.TEXT13)
             return None
         

       
    def getInfo(self):

        Logger().Log(Text.TEXT20)
        
        try:

            headers = {'content-type': "application/json"}
            url = Config.HTTP_URL + "get_info"
            r = requests.get(url)

	    if(r.status_code == 200):

       	          js = json.loads(r.text)
                  
                  if("head_block_num" in js): 
                     
                     Logger().Log(js['head_block_num'])
                     
                     if "head_block_num" in js:
                          return js['head_block_num']
                     else:
                          return -1
                  else:
                     Logger().Log('not exsit key')
                     return -1
            else:
                 Logger().Log(r.text)
                 return -1
        except:
            Logger().Log(Text.TEXT21)
            return -1
          

      
