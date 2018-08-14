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
        print "bwAction"
	try:
            voter = ""
            if(not transfer):
                 voter = frm
            else:
                 voter = receive
            
            db = MySQLdb.connect(Config.DB_SERVER, Config.DB_USER, Config.DB_PWD, Config.DB_NAME, charset='utf8' )
            cursor = db.cursor()

            staked = 0
            sql = "SELECT * FROM voters_tbl  where owner ='%s'" %(voter)
            cursor.execute(sql)
            print sql
            for row in cursor.fetchall():
                staked = row[4]

            cursor.fetchall()
      
            if(cursor.rowcount <= 0):         
                sql = "INSERT INTO voters_tbl(owner,proxy, producer,staked,is_proxy)VALUES ('%s','%s','%s',%d,%d)" %(voter,"","",total,0)
            else:
                sql = "UPDATE table voters_tbl set staked = %d where owner = '%s'" %(total + staked,voter) 
            print sql
            cursor.execute(sql)
            db.commit()    
                   
            cursor.close()
            db.close()
             
            Logger().Log(Text.TEXT70)
   
        except:
           Logger().Error(Text.TEXT71)

    def unbwAction(self,frm,total):

       try:
            db = MySQLdb.connect(Config.DB_SERVER, Config.DB_USER, Config.DB_PWD, Config.DB_NAME, charset='utf8' )
            cursor = db.cursor()

            staked = 0
            sql = "SELECT * FROM voters_tbl  where owner ='%s'" %(voter)
            cursor.execute(sql)
    
            for row in cursor.fetchall():
                staked = row[4]

            cursor.fetchall()

            if(cursor.rowcount <= 0):
                Logger().Log(Text.TEXT72)
            else:
                sql = "UPDATE table voters_tbl set staked = %d where owner = '%s'" %(staked - total,frm)

            cursor.execute(sql)
            db.commit()

            cursor.close()
            db.close() 
           
            Logger().Log(Text.Text72)
       except:
            Logger().Error(Text.TEXT73) 

    def regProxy(self,proxy,isproxy):

       try:
            db = MySQLdb.connect(Config.DB_SERVER, Config.DB_USER, Config.DB_PWD, Config.DB_NAME, charset='utf8' )
            cursor = db.cursor()

            staked = 0
            sql = "SELECT * FROM voters_tbl  where owner ='%s'" %(proxy)
            cursor.execute(sql)

            cursor.fetchall()

            if(cursor.rowcount <= 0):
                sql = "INSERT INTO voters_tbl(owner,proxy, producer,staked,is_proxy)VALUES ('%s','%s','%s',%d,%d)" %(proxy,"","",0,1)
            else:
                sql = "UPDATE table voters_tbl set is_proxy = 1  where owner = '%s'" %(proxy)

            cursor.execute(sql)
            db.commit()

            cursor.close()
            db.close()

            Logger().Log(Text.TEXT74)
       except:
            Logger().Error(Text.TEXT75)

    def regProducer(self,producer,active):
       try:
 
            db = MySQLdb.connect(Config.DB_SERVER, Config.DB_USER, Config.DB_PWD, Config.DB_NAME, charset='utf8' )
            cursor = db.cursor()

            staked = 0
            sql = "SELECT * FROM producers_tbl  where owner ='%s'" %(producer)
            
            cursor.execute(sql)
             
            cursor.fetchall()
            
            if(cursor.rowcount <= 0):
                sql = "INSERT INTO producers_tbl(owner,total_votes,is_active)VALUES ('%s',%d,%d)" %(producer,0,active)
            else:
                sql = "UPDATE producers_tbl SET is_active = %d  where owner = '%s'" %(active,producer)

            cursor.execute(sql)
            db.commit()

            cursor.close()
            db.close()

            Logger().Log(Text.TEXT76)
       except:
            Logger().Error(Text.TEXT77)

    def voteAction(self,voter,proxy,producers):

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

            cursor.fetchall()
            for row in cursor.fetchall():

                oldproxy = row[2]
                staked = row[4]
                oldproducers = row[3].split(',')
                 
                rowcount = rowcount + 1
            
            while(not oldproxy == ""):
               
               sql = "UPDATE table voters_tbl set staked = staked - %d where owner = '%s'" %(staked,oldproxy)
               cursor.execute(sql)
               
               sql ="SELECT * FROM voters_tbl  where owner ='%s'" %(oldproxy)
               cursor.execute(sql)
               cursor.fetchall()

               for row in cursor.fetchall():
                  oldproxy = row[2]
                  oldproducers = row[3].split(',')
        
               for pb in oldproducers:
                  sql =  "UPDATE table producers_tbl set total_votes  = total_votes - '%d' where owner = '%s'" %(staked,pb)
                  cursor.execute(sql)
               

            for pb in oldproducers:
                sql =  "UPDATE table producers_tbl set total_votes  = total_votes - '%d' where owner = '%s'" %(staked,pb)
                cursor.execute(sql)
                
            
             #设置相关字段 
            if(rowcount <= 0):

                if(not proxy == ""):
                   sql = "INSERT INTO voters_tbl(owner,proxy, producer,staked,is_proxy)VALUES ('%s','%s','%s',%d,%d)" %(voter,proxy,"",0,0)
                else:
                   sql = "INSERT INTO voters_tbl(owner,proxy, producer,staked,is_proxy)VALUES ('%s','%s','%s',%d,%d)" %(voter,"",",".join(producers),0,0)
            else:

                if(not proxy == ""):
                   sql = "UPDATE table voters_tbl set proxy = '%s' where owner = '%s'" %(proxy,voter) 
                else:
                   sql = "UPDATE table voters_tbl set producer = '%s' where owner = '%s'" %(",".join(producers),voter)

            cursor.execute(sql)

            #重新投票时会对新的proxy,producers加上staked
            newproxy = proxy
            newproducers = []
 
            while(not newproxy == ""):

               sql = "UPDATE table voters_tbl set staked = staked + %d where owner = '%s'" %(staked,newproxy)
               cursor.execute(sql)

               sql ="SELECT * FROM voters_tbl  where owner ='%s'" %(newproxy)
               cursor.execute(sql)
               cursor.fetchall()

               for row in cursor.fetchall():
                  newproxy = row[2]
                  newproducers = row[3].split(',')

               for pb in newproducers:
                  sql =  "UPDATE table producers_tbl set total_votes  = total_votes + '%d' where owner = '%s'" %(staked,pb)
                  cursor.execute(sql)


            for pb in newproducers:
                sql =  "UPDATE table producers_tbl set total_votes  = total_votes + '%d' where owner = '%s'" %(staked,pb)
                cursor.execute(sql)
        
            db.commit()

            cursor.close()
            db.close()

            Logger().Log(Text.TEXT78)

       except:
            Logger().Error(Text.TEXT79)
