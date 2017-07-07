#coding=utf-8
import MySQLdb
import datetime
import time

conn = MySQLdb.Connect(
                       host = '127.0.0.1',
                       port = 3306,
                       user = 'root',
                       passwd = '940308',
                       db = 'test',
                       charset = 'utf8'
                       )

cursor = conn.cursor()

a = '300'
b = '300'
d = '2006-05-18 20:10:10'
t = time.strptime(d, "%Y-%m-%d %H:%M:%S")
da_time = datetime.datetime(*t[:6])
print da_time
sql = "select time from test where id=1"
cursor.execute(sql)
rs = cursor.fetchone()[0]
if da_time>rs:
    print False
else:
    print True 
cursor.close()
conn.close()
