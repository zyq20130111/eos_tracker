# -*- coding: utf-8 -*-
# filename: handle.py
import hashlib
import receive
import web
from  logger import Logger
from text import Text
import reply

class Handle(object):

    def GET(self):
        try:
            data = web.input()
            if len(data) == 0:
                return "hello, this is handle view"
        except Exception, Argument:
            return Argument

    def POST(self):
        try:
            webData = web.data()

            Logger().Log(webData)  #后台打日志
            recMsg = receive.parse_xml(webData)

            if isinstance(recMsg, receive.Msg):
		print "xxx"
            else:
                print "暂且不处理"
        except Exception, Argment:
            return Argment
