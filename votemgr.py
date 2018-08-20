#/usr/bin/python
# -*- coding: UTF-8 -*-         

import MySQLdb
from config import Config
from text import Text
from logger import Logger

class VoteMgr(object):

    __instance = None

    def __init__(self):
       pass

    def __new__(cls, *args, **kwargs):
       if not VoteMgr.__instance:
           VoteMgr.__instance = object.__new__(cls,*args, **kwargs)
       return VoteMgr.__instance

    def Instance(self):
        return VoteMgr.__instance

    def bwAction(self,frm,receive,total,transfer):
        print "bwAction",frm,receive,total,transfer        
	try:
            voter = ""
            if(transfer ==  0):
                 voter = frm
            else:
                 voter = receive
            
            db = MySQLdb.connect(Config.DB_SERVER, Config.DB_USER, Config.DB_PWD, Config.DB_NAME, charset='utf8' )
            cursor = db.cursor()

            staked = 0
            sql = "SELECT * FROM voters_tbl  where owner ='%s'" %(voter)
            cursor.execute(sql)
           
            for row in cursor.fetchall():
                staked = row[4]

            cursor.fetchall()
      
            if(cursor.rowcount <= 0):         
                sql = "INSERT INTO voters_tbl(owner,proxy, producer,staked,is_proxy,total_proxy)VALUES ('%s','%s','%s',%d,%d,%d)" %(voter,"","",total,0,0)
            else:
                sql = "UPDATE voters_tbl SET staked = %d where owner = '%s'" %(total + staked,voter) 
            print sql
            cursor.execute(sql)

            #投票者相关字段，重新投票时会对原有的proxy,producers减去staked
            sql = "SELECT * FROM voters_tbl  where owner ='%s'" %(voter)
            cursor.execute(sql)

            oldproxy = ""
            oldproducers = []
            is_proxy = 0
            for row in cursor.fetchall():

                oldproxy = row[2]
                oldproducers = row[3].split(',')
                is_proxy = row[5]

            self.vote(cursor,oldproxy,oldproducers,total,total)

            db.commit()    
                   
            cursor.close()
            db.close()
             
            Logger().Log(Text.TEXT70)
   
        except:
           Logger().Error(Text.TEXT71)

    def unbwAction(self,frm,total):
       print "unbwAction",frm,total
       try:

            db = MySQLdb.connect(Config.DB_SERVER, Config.DB_USER, Config.DB_PWD, Config.DB_NAME, charset='utf8' )
            cursor = db.cursor()
                        
            staked = 0
            sql = "SELECT * FROM voters_tbl  where owner ='%s'" %(frm)
            cursor.execute(sql)
                
            for row in cursor.fetchall():
                staked = row[4]
   
                     
            cursor.fetchall()

            if(cursor.rowcount <= 0):
                Logger().Log(Text.TEXT72)
                return
            else:
                sql = "UPDATE  voters_tbl SET staked = %d where owner = '%s'" %(staked - total,frm)
             
            cursor.execute(sql)
            print sql
            #投票者相关字段，重新投票时会对原有的proxy,producers减去staked
            sql = "SELECT * FROM voters_tbl  where owner ='%s'" %(frm)
            cursor.execute(sql)
            
            oldproxy = ""
            oldproducers = []
                
            for row in cursor.fetchall():

                oldproxy = row[2]
                oldproducers = row[3].split(',')
            print "tttttt"
            self.vote(cursor,oldproxy,oldproducers,-total,-total)

            db.commit()
            

            cursor.close()
            db.close() 
           
            Logger().Log(Text.TEXT72)
       except:
            Logger().Error(Text.TEXT73) 

    def regProxy(self,proxy,isproxy):
       print "regProxy",proxy,isproxy
       try:

            db = MySQLdb.connect(Config.DB_SERVER, Config.DB_USER, Config.DB_PWD, Config.DB_NAME, charset='utf8' )
            cursor = db.cursor()

            staked = 0
            sql = "SELECT * FROM voters_tbl  where owner ='%s'" %(proxy)
            cursor.execute(sql)

            cursor.fetchall()

            if(cursor.rowcount <= 0):
                sql = "INSERT INTO voters_tbl(owner,proxy, producer,staked,is_proxy,total_proxy)VALUES ('%s','%s','%s',%d,%d,%d)" %(proxy,"","",0,1,0)
            else:
                sql = "UPDATE  voters_tbl set is_proxy = %d  where owner = '%s'" %(isproxy,proxy)

            cursor.execute(sql)
            print sql
            #投票者相关字段，重新投票时会对原有的proxy,producers减去staked
            staked = 0
            sql = "SELECT * FROM voters_tbl  where owner ='%s'" %(proxy)
            cursor.execute(sql)
            
            row = cursor.fetchone();

            total_proxy = row[6]
              
            if(isproxy == 0):
                 sql = "UPDATE  voters_tbl set staked = staked - %d  where owner = '%s'" %(total_proxy,proxy)
                 cursor.execute(sql)

                 proxy = row[2]
                 producers = row[3].split(',')
            
                 self.vote(cursor,proxy,producers,-total_proxy,0)
            else:
                 sql = "UPDATE  voters_tbl set staked = staked + %d  where owner = '%s'" %(total_proxy,proxy)
                 cursor.execute(sql)

                 proxy = row[2]
                 producers = row[3].split(',')

                 self.vote(cursor,proxy,producers,total_proxy,0)

            db.commit()

            cursor.close()
            db.close()

            Logger().Log(Text.TEXT74)
       except:
            Logger().Error(Text.TEXT75)

    def regProducer(self,producer,active,staked):
       print "regProducer",producer,active,staked
       try:
          
            db = MySQLdb.connect(Config.DB_SERVER, Config.DB_USER, Config.DB_PWD, Config.DB_NAME, charset='utf8' )
            cursor = db.cursor()

            staked = 0
            sql = "SELECT * FROM producers_tbl  where owner ='%s'" %(producer)
            
            cursor.execute(sql)
             
            cursor.fetchall()
            
            if(cursor.rowcount <= 0):
                sql = "INSERT INTO producers_tbl(owner,total_votes,is_active)VALUES ('%s',%d,%d)" %(producer,staked,active)
            else:
                sql = "UPDATE producers_tbl SET is_active = %d,total_votes = %d  where owner = '%s'" %(active,staked,producer)
            print sql
            cursor.execute(sql)
            db.commit()

            cursor.close()
            db.close()

            Logger().Log(Text.TEXT76)
       except:
            Logger().Error(Text.TEXT77)

    def vote(self,cursor,proxy,producers,staked,proxy_staked):
        print "vote",proxy,producers,staked,proxy_staked
        try:
            stopStake = 0
            
            while(not proxy == ""):
              
               is_proxy  = 0
               producers = []
               newproxy = ""
                
               #如果是proxy,更新total_proxy
               sql = "SELECT * FROM voters_tbl  where owner ='%s'" %(proxy)
               cursor.execute(sql)

               for row in cursor.fetchall():
                  is_proxy = row[5]
                  newproxy = row[2]
                  producers = row[3].split(',')

               #更新staked
               if((is_proxy == 1) and (stopStake == 0)):
                  sql = "UPDATE  voters_tbl set staked = staked + %d where owner = '%s'" %(staked,proxy)
                  cursor.execute(sql)
                  print sql,"11111"
               else:
                   stopStake = 1
               
 
               sql = "UPDATE  voters_tbl set total_proxy = total_proxy + %d where owner = '%s'" %(proxy_staked,proxy)
               cursor.execute(sql)
               print sql,"22222"
               #处理下一个代理
               proxy = newproxy

               #处理producers
               for pb in producers:
                  if(not (pb == "")):
                     sql =  "UPDATE  producers_tbl set total_votes  = total_votes + '%d' where owner = '%s'" %(staked,pb)
                     cursor.execute(sql)
                     print sql,"3333"
               
               return 

            #处理producers
            for pb in producers:
                if(not (pb == "")):
                    sql =  "UPDATE producers_tbl set total_votes  = total_votes + '%d' where owner = '%s'" %(staked,pb)
                    print sql,"44444"
                    cursor.execute(sql)
        except:
             print "error"

    def voteAction(self,voter,proxy,producers):
       print "voteAction",voter,proxy,producers    
       try:
           
            db = MySQLdb.connect(Config.DB_SERVER, Config.DB_USER, Config.DB_PWD, Config.DB_NAME, charset='utf8' )
            cursor = db.cursor()
            rowcount = 0

            #投票者相关字段，重新投票时会对原有的proxy,producers减去staked          
            staked = 0
            sql = "SELECT * FROM voters_tbl  where owner ='%s'" %(voter)      
            cursor.execute(sql)
      
            staked = 0
            oldproxy = ""
            oldproducers = []

            for row in cursor.fetchall():
                
                oldproxy = row[2]
                staked = row[4]
                oldproducers = row[3].split(',')
                is_proxy = row[5]
                rowcount = rowcount + 1

            self.vote(cursor,oldproxy,oldproducers,-staked,-staked) 
            
             #设置相关字段 
            if(rowcount <= 0):
                
                if(not proxy == ""):
                   sql = "INSERT INTO voters_tbl(owner,proxy, producer,staked,is_proxy,total_proxy)VALUES ('%s','%s','%s',%d,%d,%d)" %(voter,proxy,"",0,0,0)
                else:
                   sql = "INSERT INTO voters_tbl(owner,proxy, producer,staked,is_proxy,total_proxy)VALUES ('%s','%s','%s',%d,%d,%d)" %(voter,"",",".join(producers),0,0,0)
            else:
                
                if(not proxy == ""):
                   sql = "UPDATE  voters_tbl set proxy = '%s' where owner = '%s'" %(proxy,voter) 
                else:
                   sql = "UPDATE  voters_tbl set producer = '%s' where owner = '%s'" %(",".join(producers),voter)
           
            print "5555",sql
            cursor.execute(sql)

            #重新投票时会对新的proxy,producers加上staked
            newproxy = proxy
            newproducers = producers
            
            self.vote(cursor,newproxy,newproducers,staked,staked)
 
            db.commit()

            cursor.close()
            db.close()

            Logger().Log(Text.TEXT78)

       except:
            Logger().Error(Text.TEXT79)
