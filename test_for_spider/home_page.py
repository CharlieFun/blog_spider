#coding=utf-8

import urllib2
import random
import MySQLdb
import requests
import re
import blogs
from lxml import html



class Home:
    def __init__(self,conn):
        self.home_page = "http://blog.sina.com.cn/"
        self.conn = conn
        self.headers1 = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36"}
        self.headers2 = {"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50"}
        self.headers3 = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0"}
        self.headers4 = {"User-Agent":"Opera/9.80 (Windows NT 5.1; U; zh-cn) Presto/2.9.168 Version/11.50"}
        self.headers5 = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36 LB"}
        self.headerlist = [self.headers1,self.headers2,self.headers3,self.headers4,self.headers5]
    
    
    def open_url(self,url):
        headers = random.choice(self.headerlist)
        request = urllib2.Request(url,headers = headers)
        try:
            response = urllib2.urlopen(request,timeout=8) 
        except Exception,e:
            print e 
            return False
        else: 
            try:
                content = response.read().decode('utf-8') 
            except Exception,e2:
                print e2
                return False
            else: 
                return content
            
            
    def getArticlePage(self,url):
        headers = random.choice(self.headerlist)
        page=requests.get(url,headers = headers,timeout = 6)
        page.encoding='utf-8'
        tree=html.fromstring(page.text)
        return tree
            
    
    def legal_url(self,url):
        tree = self.getArticlePage(url)
        person_xpath = '//div[@class="headBox"]/h1/span/a/@href'
        listUrl_xpath = '//div[@class="blognavInfo"]/span[2]/a/@href' #博文目录
        try:
            listUrl = tree.xpath(listUrl_xpath)[0]
        except:
            try:
                person_url = tree.xpath(person_xpath)[0]
            except:
                return False
            else:
                return person_url
        else:
            return listUrl
        
        
    def get_uid(self, url):
        tree = self.getArticlePage(url)
        info_url_path = '//div[@class="blognavInfo"]/span[@class="last"]/a/@href'
        info_url = tree.xpath(info_url_path)[0]
        uid1 = re.split("_",info_url)[1]
        uid = re.split("\.",uid1)[0]
        return uid
        
        
    def main(self):
        content = self.open_url(self.home_page)
        urls=re.findall(r'"(http://blog.sina.com.cn/s/.+?\.html\?tj=1)"',content)
        for x in urls:
            try:
                url = self.legal_url(x)
                if not url:
                    continue
                else:
                    uid = self.get_uid(url)
                    print uid
                    cursor = self.conn.cursor()
            except Exception as e1:
                print e1
                continue
            else:
                try:
                    sql_insert = "insert into test(uid) values (%s)" % uid
                    cursor.execute(sql_insert)
                    self.conn.commit()
                except:
                    self.conn.rollback()
                finally:
                    cursor.close()
                    blog = blogs.Blog(url,self.conn)
                    blog.main()
                        
        
            







if __name__=="__main__":
    conn = MySQLdb.Connect(
                           host = '127.0.0.1',
                           port = 3306,
                           user = 'root',
                           passwd = '940308',
                           db = 'test',
                           charset = 'utf8'
                           )
    
    home = Home(conn)
    try:
        home.main()
    except Exception as e:
        print e
    finally:
        conn.close()
    
        