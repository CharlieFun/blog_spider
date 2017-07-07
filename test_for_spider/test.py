#coding=utf-8
import urllib2
import re
from time import sleep

headers1 = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36"}
url = "http://blog.sina.com.cn/"
request = urllib2.Request(url,headers = headers1)
response = urllib2.urlopen(request,timeout=8)
content = response.read().decode('utf-8')
urls=re.findall(r'"(http://blog.sina.com.cn/s/.+?\.html\?tj=1)"',content)
for i in urls:
    print i
    sleep(3)