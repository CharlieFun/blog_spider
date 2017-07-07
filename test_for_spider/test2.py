#coding=utf-8

import re 
import MySQLdb
import urllib2

conn = MySQLdb.Connect(
                           host = '127.0.0.1',
                           port = 3306,
                           user = 'root',
                           passwd = '940308',
                           db = 'test',
                           charset = 'utf8'
                           )

sql = "select update_time from uids where id = 1"
cursor = conn.cursor()
cursor.execute(sql)
a=cursor.fetchone()[0]
print a 
print type(a)
cursor.close()

conn.close()
