#coding=utf-8

from lxml import html
import random
import urllib2  
import urllib 
import tools
import requests
import re  
import os
import sys  
import MySQLdb
import time
import datetime
reload(sys)  
sys.setdefaultencoding('utf-8') 

class Blog:
    def __init__(self,personUrl,conn):
        self.tool = tools.Tool()
        self.personUrl = personUrl
        self.conn = conn
        self.blogname = None
        self.uid = None
        self.update_time = None
        self.headers1 = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36"}
        self.headers2 = {"User-Agent":"Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50"}
        self.headers3 = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64; rv:41.0) Gecko/20100101 Firefox/41.0"}
        self.headers4 = {"User-Agent":"Opera/9.80 (Windows NT 5.1; U; zh-cn) Presto/2.9.168 Version/11.50"}
        self.headers5 = {"User-Agent":"Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/42.0.2311.152 Safari/537.36 LB"}
        self.headerlist = [self.headers1,self.headers2,self.headers3,self.headers4,self.headers5]
        
        
    #得到文章列表第一面的内容  
    def getArticlePage(self,url):
#         print url
        headers = random.choice(self.headerlist)
        page=requests.get(url,headers = headers,timeout = 6)
        page.encoding='utf-8'
        tree=html.fromstring(page.text)
        return tree
    
    #获取评论数，转载数
    def extra_content(self,url):
        extra_url = "http://comet.blog.sina.com.cn/api?maintype=num&uid={}&aids={}"
        url_string = re.split("_",url)
        string1 = url_string[1][:8]
        string2 = url_string[1][10:16]
        url2 = extra_url.format(string1,string2)
        #request = urllib2.Request(url2,headers=random.choice(self.headerlist))
        request = urllib2.Request(url2,headers=self.headers1)
        try:  
            response = urllib2.urlopen(request,timeout=8)
        except Exception,e:
            print e 
            return False
        else:  
            content = response.read() 
            nums = []
            read_num = re.search('"r":(\d+)',content).group(1)
            nums.append(read_num)
            comment_num = re.search('"c":(\d+)', content).group(1)
            nums.append(comment_num)
            collect_num = re.search('"f":(\d+)',content).group(1)
            nums.append(collect_num)
            zhuanzai_num = re.search('"z":(\d+)',content).group(1)
            nums.append(zhuanzai_num)
            return nums
    
    
    
    #得到列表第一面中所有链接信息  
    def getLink(self,url):  
        tree = self.getArticlePage(url)
        link_xpath = '//span[@class="atc_title"]/a/@href'       
        links=tree.xpath(link_xpath)
        return links
    
  
    
    #通过URL得到文章内容  
    def getArticleDetail(self,ArticleUrl): 
        headers = random.choice(self.headerlist)   
        request = urllib2.Request(ArticleUrl,headers=headers)
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
    
    #通过内容筛选出文章并且保存起来  
    def get_content(self,content): 
        try: 
            pattern = re.compile('<div.*?id="sina_keyword_ad_area2".*?>(.*?)<div class="share SG_txtb">',re.S)  
            result = re.search(pattern,content).group(1)
        except:
            pattern = re.compile('<div.*?id="sina_keyword_ad_area2".*?>(.*?)</div>',re.S) 
            result = re.search(pattern,content).group(1) 
        finally: 
            result = self.tool.replace(result)
            return result
        
        
        
    def clean_blog_title(self,blog_title):
        blog_title=re.sub(r'\*','',blog_title)
        blog_title=re.sub(r'\\','',blog_title)
        blog_title=re.sub(r'\/','',blog_title)
        blog_title=re.sub(r'\:','',blog_title)
        blog_title=re.sub(r'\?','',blog_title)
        blog_title=re.sub(r'\"','',blog_title)
        blog_title=re.sub(r'\<','',blog_title)
        blog_title=re.sub(r'\>','',blog_title)
        blog_title=re.sub(r'\|','',blog_title)
        return blog_title
    
    
    
    def get_last(self, content):
        blog_type = 1
        try:
            blog_title_pattern1 = re.compile('class="h1_tit".*?>(.*?)</',re.S)
            blog_title = re.search(blog_title_pattern1,content).group(1)
        except:
            blog_title_pattern2 = re.compile('class="titName SG_txta".*?>(.*?)</',re.S)
            blog_title = re.search(blog_title_pattern2,content).group(1)
#         from_uid_pattern = re.compile('<div class="blogzz_ainfo".*?href="(.*?)".*?</div>',re.S)
            from_uid_pattern = re.compile('<div class="blogzz_ainfo"(.*?)</div>',re.S)
            time_pattern = re.compile('class="time SG_txtc">(.*?)</span>',re.S)
            from_uid_content = re.findall(from_uid_pattern,content)
            blog_time = re.search(time_pattern,content).group(1)
            blog_time = re.findall(r'\((.*?)\)',blog_time)[0]
            if from_uid_content:
                blog_type = 0
#                 from_uid_s = re.findall(r'href="(.*?)"',from_uid_content[0])
#                 from_uid_url = from_uid_s[1]
#                 print from_uid_url
#                 print from_uid_content
                from_uid_url = re.findall(r'作者：.*?href="(.*?)"',from_uid_content[0].encode('utf-8'))[0]
#                 print from_uid_url
                from_uid = re.search(r'/u/(\d+)',from_uid_url).group(1)
                return blog_title,blog_time,blog_type,from_uid
            else:
                from_uid = '0'
                return blog_title,blog_time,blog_type,from_uid
        else:
            from_uid_pattern = re.compile('<a TARGET="_blank"(.*?)</A></SPAN></DIV>',re.S)
            time_pattern = re.compile('class="time SG_txtc">(.*?)</span>',re.S)
            from_uid_content = re.findall(from_uid_pattern,content)
#             print content
#             print from_uid_content
            blog_time = re.search(time_pattern,content).group(1)
            if from_uid_content:
                blog_type = 0
#                 print "blog_type="+str(blog_type)
                from_uid_s = re.findall(r'HREF="(.*?)"',from_uid_content[0])
                from_uid_url = from_uid_s[1]
                from_uid = re.search(r'/u/(\d+)',from_uid_url).group(1)
                return blog_title,blog_time,blog_type,from_uid
            else:
                from_uid = '0'
                return blog_title,blog_time,blog_type,from_uid
            
            
            
            
    def mkdir(self,path):  
        path = path.strip()  
        isExits = os.path.exists(path)  
        if not isExits:  
            print u"创建了新的文件夹叫做",path  
            os.makedirs(path)  
            return True  
        else:  
            print u"名为",path,"的文件夹已经存在"  
            return True
        
        
        
    def save_article(self,blog_content,blog_title,blog_time,blog_type,from_uid,extra_content,path):
        fileName = "{}/{}.txt".format(path,blog_title).decode('utf-8') 
#         print blog_type,from_uid
        try:
            with open(fileName,"w+") as f:
                f.write("博主uid：")
                f.write(self.uid)
                f.write('\n')
                f.write(blog_title)
                f.write('\n')
                f.write(blog_time)
                f.write('\n')
                f.write("文章类型：")
                f.write(str(blog_type)) 
                f.write('\n')
                f.write("转载uid：")
                f.write(from_uid) 
                f.write('\n')
                f.write("阅读：")
                f.write(extra_content[0])
                f.write('\n')
                f.write("评论：")
                f.write(extra_content[1])
                f.write('\n')
                f.write("收藏：")
                f.write(extra_content[2])
                f.write('\n') 
                f.write("转载：")
                f.write(extra_content[3])
                f.write('\n')  
                f.write(blog_content.encode('utf-8'))  
        except Exception as e:
            print e
            
    
    
    
    #通过url下载当页的50篇文章 
    def downloadByURL(self,url,mysql_update_time,path): 
        links = self.getLink(url)
        for link in links:  
            page_content = self.getArticleDetail(link) 
            extra_content = self.extra_content(link) 
            if ((page_content==False) or (extra_content==False)):
                continue
            else:
                blog_content = self.get_content(page_content)
                blog_title,blog_time,blog_type,from_uid = self.get_last(page_content)
                print blog_title
                blog_title = self.clean_blog_title(blog_title)
#                 if int(from_uid) != 0:
#                     cursor2 = self.conn.cursor()
#                     try:
#                         sql_insert2 = "insert into test(uid) values (%s)" % from_uid
#                         cursor2.execute(sql_insert2)
#                         self.conn.commit()
#                     except:
#                         self.conn.rollback()
#                     finally:
#                         cursor2.close()   
                if blog_type == 1:
                    if extra_content[3] != 0:
                        blogid = re.split("_",link)[1][:16]
                        zurl = "http://control.blog.sina.com.cn/myblog/htmlsource/quotelist.php?blogid=%s&version=7&page={}" % blogid
                        if int(extra_content[3])%10 == 0:
                            num = int(extra_content[3])/10
                        else:
                            num = int(extra_content[3])/10+1
                        for i in xrange(num):
                            zzurl = zurl.format(i+1)
                            request = urllib2.Request(zzurl,headers=self.headers1)
                            try:  
                                response = urllib2.urlopen(request,timeout=8)
                            except Exception,e:
                                print e 
                            else:  
                                content = response.read() 
                                zzuids = re.findall('"rp_bloguid":"(\d+)"',content)
                                for j in zzuids:
                                    cursor = self.conn.cursor()
                                    try:
                                        sql_insert = "insert into test(uid) values (%s)" % j
                                        cursor.execute(sql_insert)#还要判断uid是否已存在，什么时候conn.commit,所有时间事件完成后要将mysql中update_time更新
                                        self.conn.commit()
                                    except Exception as e2:
                                        self.conn.rollback()
#                                         print e2 
                                    finally:
                                        cursor.close() 
                struct_blog_time = time.strptime(blog_time, "%Y-%m-%d %H:%M:%S")
                datetime_blog_time = datetime.datetime(*struct_blog_time[:6])
                if datetime_blog_time > mysql_update_time:
                    self.save_article(blog_content,blog_title,blog_time,blog_type,from_uid,extra_content,path)
                    continue
                else:
                    time.sleep(random.randint(1,3))
                    return False
        time.sleep(random.randint(1,5))
        return True
                
                
                    
                
#                 print blog_title,blog_time,blog_type,from_uid,extra_content
#                 print self.blogname,self.uid
                #加上一个important_uid字段!!!
                #sleep(random.randint(1,5))
                #sleep(5)
            
    #查找下一页
    def nextPage(self,url):
        tree = self.getArticlePage(url)
        next_xpath = '//li[@class="SG_pgnext"]/a/@href' 
        nextPageUrl = tree.xpath(next_xpath)
        if nextPageUrl:
            return nextPageUrl[0]
        else:
            return False 
        
                
    # 获取uid和博主名      
    def get_info(self, url):
        tree = self.getArticlePage(url)
        info_url_path = '//div[@class="blognavInfo"]/span[@class="last"]/a/@href'
        info_url = tree.xpath(info_url_path)[0]
        uid1 = re.split("_",info_url)[1]
        self.uid = re.split('\.',uid1)[0]
        tree2 = self.getArticlePage(info_url)
        blogname_xpath = '//span/strong[@id="ownernick"]/text()'
        blogname = tree2.xpath(blogname_xpath)[0]
        self.blogname= blogname.strip()
    
    
    def main(self):    
        try:
            personTree = self.getArticlePage(self.personUrl)
            listUrl_xpath = '//div[@class="blognavInfo"]/span[2]/a/@href' #博文目录
            listUrl = personTree.xpath(listUrl_xpath)[0]
        except:
            print "该博客出现问题"
        else:
            cursor = self.conn.cursor()
            self.get_info(self.personUrl)   #获取uid和博主
            folderPath="D:/code/blog/{}".format(self.blogname).decode('utf-8')
            self.mkdir(folderPath)
            firstblog_link = self.getLink(listUrl)[0]
            firstblog_page_content = self.getArticleDetail(firstblog_link)
            if firstblog_page_content == False:
                print "main函数结束"
                return False
            firstblog_title,firstblog_time,firstblog_type,firstfrom_uid = self.get_last(firstblog_page_content)
            self.update_time = firstblog_time
            sql_time = "select update_time from test where uid=%s" % self.uid
            cursor.execute(sql_time)
            mysql_update_time = cursor.fetchone()[0]
            print "上一次最新博客时间为%s" % mysql_update_time
            print "现在最新博客时间为%s" % firstblog_time
            sql_update = "update test set update_time='%s' where uid=%s"%(self.update_time,self.uid)
            try:
                cursor.execute(sql_update)
                self.conn.commit()
            except Exception as e2:
                print e2
                self.conn.rollback()
            finally:
                cursor.close()
            
            flag1 = self.downloadByURL(listUrl,mysql_update_time,folderPath)  #获取用户第一页的文章
            if not flag1:
                print "更新结束"
                return True
            else:
    #循环获取用户所有页的文章
                nextPageUrl = self.nextPage(listUrl)
                while nextPageUrl:
                    flag2 = self.downloadByURL(nextPageUrl,mysql_update_time,folderPath)
                    if not flag2:
                        print "更新结束"
                        return True
                    else:
                        nextPageUrl = self.nextPage(nextPageUrl) 
                return True
    
    
    
    
    def main_test(self):    
        try:
            personTree = self.getArticlePage(self.personUrl)
            listUrl_xpath = '//div[@class="blognavInfo"]/span[2]/a/@href' #博文目录
            listUrl = personTree.xpath(listUrl_xpath)[0]
        except:
            raise Exception("该博客出现问题") 
        else:
            self.get_info(self.personUrl)   #获取uid和博主
            self.downloadByURL(listUrl)
            
if __name__=="__main__": 
    conn = MySQLdb.Connect(
                           host = '127.0.0.1',
                           port = 3306,
                           user = 'root',
                           passwd = '940308',
                           db = 'test',
                           charset = 'utf8'
                           )
    id = 1
    while True:
        cursor = conn.cursor()
        sql = "select uid from test where id=%s" % id
        cursor.execute(sql)
        result = cursor.fetchall()
        if len(result) != 1:
            id = id+1
            cursor.close()
            print "表中没有此id"
            continue
        uid = result[0][0]
        cursor.close()
        uid_url = "http://blog.sina.com.cn/u/%s" % uid
        blog = Blog(uid_url,conn)
        blog.main()
        id = id+1
    conn.close()