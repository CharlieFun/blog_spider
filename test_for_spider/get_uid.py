#coding=utf-8
import requests
import re
from lxml import html
import MySQLdb
import random
from time import sleep
#import sys
#reload(sys)
#sys.setdefaultencoding('utf-8') 

urls = 'http://blog.sina.com.cn/u/{}'
headers1 = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36"}
headers2 = {"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50"}
headers3 = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0"}
headers4 = {"User-Agent":"Opera/9.80 (Windows NT 5.1; U; zh-cn) Presto/2.9.168 Version/11.50"}
headers5 = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36 LB"}
headerlist = [headers1,headers2,headers3,headers4,headers5]

stop_count = 0


def get_page(url):
    headers = random.choice(headerlist)
    timeout = random.randint(6,10)
    try:
        page = requests.get(url,headers = headers,timeout = timeout)
        page.encoding = 'utf-8'
        tree = html.fromstring(page.text)
        return tree
    except Exception as e:
        print e
        global stop_count
        stop_count = stop_count+1
        if stop_count<5:
            return None
        else:
#             stop_time = random.randint(20,30)
#             sleep(stop_time)
            sleep(3)
            global stop_count
            stop_count = 0
            return None

# tree = get_page(url)
# info_url_path = '//div[@class="blognavInfo"]/span[@class="last"]/a/@href'
# info_url = tree.xpath(info_url_path)[0]
# uid = re.split("_",info_url)[1][:10]
# print uid
# tree2 = get_page(info_url)
# blogname_xpath = '//span/strong[@id="ownernick"]/text()'
# blogname = tree2.xpath(blogname_xpath)[0]
# blogname= blogname.strip()
# print blogname

if __name__=="__main__":
    uid = 1020436000
    num = 0
    conn = MySQLdb.Connect(
                           host = '127.0.0.1',
                           port = 3306,
                           user = 'root',
                           passwd = '940308',
                           db = 'spider',
                           charset = 'utf8'
                           )
    
    
    
    while num < 20000:
        count = 0
        while count<20:
            cursor = conn.cursor()
            url = urls.format(uid)
            tree = get_page(url)
            listUrl_xpath = '//div[@class="blognavInfo"]/span[2]/a/@href'
            try:
                listUrl = tree.xpath(listUrl_xpath)[0]
            except Exception as e:
                print "博客%s不存在" % uid
            else:
                print "正在插入"
                sql = "insert into uids(uid) values (%s)" % uid
                try:
                    cursor.execute(sql)
                    conn.commit()
                    print "插入成功"
                except:
                    conn.rollback()
            finally:
                num = num+1
                count = count+1
                uid = uid+1
                cursor.close()
        sleep_time = random.randint(2,5)
        print "停%s秒" % sleep_time
        sleep(sleep_time)
        
            
    conn.close()
    print "运行结束！"
        

