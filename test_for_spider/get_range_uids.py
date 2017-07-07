#coding=utf-8

from lxml import html
from time import sleep
import urllib2  
import urllib 
import tools
import blogs
import requests
import re  
import os
import sys  
import MySQLdb
reload(sys)  
sys.setdefaultencoding('utf-8') 

def get_uids(url):
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36"}
    page = requests.get(url,headers = headers)
    page.encoding = 'gbk'
    tree = html.fromstring(page.text)
#     blognames_xpath = '//tr/td[@class="link335bbd"][2]/a/text()'
    bloghrefs_xpath = '//tr/td[@class="link335bbd"][2]/a/@href'
#     blognames = tree.xpath(blognames_xpath)
    bloghrefs = tree.xpath(bloghrefs_xpath)
    uids = []
    for i in xrange(len(bloghrefs)):
        uid = re.split("/u/",bloghrefs[i])[1]
        uids.append(uid)
    return uids
    

if __name__=="__main__":
    originalUrl = 'http://blog.sina.com.cn/lm/iframe/top/alltop_more_new_{}.html'
    uids = []
    for i in xrange(1,11):
        tempUrl = originalUrl.format(i)
        uids_to_extend = get_uids(tempUrl)
        uids.extend(uids_to_extend)
    conn = MySQLdb.Connect(
                           host = '127.0.0.1',
                           port = 3306,
                           user = 'root',
                           passwd = '940308',
                           db = 'test',
                           charset = 'utf8'
                           )
    
    cursor = conn.cursor()
    for j in xrange(len(uids)):
        sql = "insert into uid(uid) values (%s)" % uids[j]
        try:
            cursor.execute(sql)
            conn.commit()
        except:
            conn.rollback()
    
    cursor.close()
    conn.close()
    print "Yes!"
        
        
        
#         blog = blogs.Blog()
#         for blogInfo in blogInfos:
#             blog.blogname = blogInfo[0]
#             blog.personUrl = blogInfo[1]
#             blog.main()
        
     
    