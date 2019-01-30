
# coding: utf-8

# In[1]:


from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup

import datetime 
import pymysql


# In[2]:


def createDB(conn,dbname):
    curs = conn.cursor()
    query = """CREATE DATABASE """+dbname
    try :
        curs.execute(query)
    except :
        print('DB가 이미 존재합니다. DB_NAME : ',dbname)
    
    query = """ALTER DATABASE """+ dbname + """ CHARACTER SET utf8 COLLATE utf8_general_ci;"""
    curs.execute(query)
    conn.commit()


# In[3]:


def save_DB() : 
    temp = keyword.replace(' ','_')
    conn = pymysql.connect(host = "", user = "root", password = "", charset = "utf8")
    dbname = 'naver_blog_'+ temp
    createDB(conn,dbname)
    curs = conn.cursor()
    curs.execute("""use """+dbname)

    query = """CREATE TABLE IF NOT EXISTS """+ temp + """(ID int, URL varchar(100), Title varchar(100), Date varchar(20), Writer varchar(50), blog_like int, Count int,Text text(62200));"""
    curs.execute(query)

    query = """ALTER TABLE """ + temp +""" CHARACTER SET utf8 COLLATE utf8_general_ci;"""
    curs.execute(query)

    conn.commit()
    
    select_query = """SELECT * from """ + temp
    index = curs.execute(select_query)

    for value in total_list :
        url = value[0]
        title = value[1]
        date = value[2]
        writer = value[3]
        like = value[4]
        count = value[5]
        content = value[6]

        query = """insert into """ + temp + """(ID, URL, Title, Date, Writer, blog_like, Count, Text) values (%s, %s, %s, %s, %s, %s, %s, %s) ; """
        curs.execute(query, (str(index), url, title, date,writer,like,count,content))

        index = index + 1 

        conn.commit()
        
    conn.close()
    print("FINISH")


# In[4]:


import re

INVISIBLE_ELEMS = ('style', 'script', 'head', 'title')
RE_SPACES = re.compile(r'\s{3,}')

def visible_texts(soup):
    text = ' '.join([
        s for s in soup.strings
        if s.parent.name not in INVISIBLE_ELEMS
    ])

    return RE_SPACES.sub('  ', text)


# In[5]:


keyword = input("Keyword ? ")

start_year = input("Start Year ? ")
start_month = input("Start Month ? ")
start_day = input("Start Day ? ")

end_year = input("End Year ? ")
end_month = input("End Month ? ")
end_day = input("End Day ? ")

start_date = start_year+start_month+start_day
end_date = end_year+end_month+end_day


# In[8]:


dt_start_date = datetime.datetime.strptime(start_date,"%Y%m%d").date()
dt_end_date = datetime.datetime.strptime(end_date,"%Y%m%d").date()
day_1 = datetime.timedelta(days=1)
dt_start_1 = dt_start_date

# 일수를 하루씩 잘라서 반복
while dt_start_1 <= dt_end_date :
    total_list = []
    URL_date_list = []
    page_num = 0
    print(dt_start_1)
    # 페이지 만큼 돌면서 링크 수집
    while True : 
        p_url = 'https://search.naver.com/search.naver?where=post&query='+keyword+'&st=sim&sm=tab_opt&date_from='+start_date+'&date_to='+start_date+'&date_option=8&srchby=all&dup_remove=1&mson=0&start='+str(page_num)+'1'
        driver = webdriver.Chrome('./chromedriver/chromedriver')
        driver.implicitly_wait(3)
        driver.get(p_url)
        soup = BeautifulSoup(driver.page_source,'html.parser')

        a_tags = soup.select('ul#elThumbnailResultArea li dl dt a')

        # 한 페이지에 있는 링크들 전부 가져오기
        for a in a_tags :
            if 'href' in a.attrs :
                if 'blog.me' in a.attrs['href'] or 'blog.naver.com' in a.attrs['href'] :
                    url = a.attrs['href']
                    driver = webdriver.Chrome('./chromedriver/chromedriver')
                    driver.implicitly_wait(3)
                    driver.get(url)

                    # 페이지 변환
                    if 'blog.me' in url :        
                        frame =driver.find_element_by_name('screenFrame')
                        driver.switch_to_frame(frame)
                        frame =driver.find_element_by_name('mainFrame')
                        driver.switch_to_frame(frame)
                    else :
                        frame =driver.find_element_by_name('mainFrame')
                        driver.switch_to_frame(frame)

                    soup = BeautifulSoup(driver.page_source,'html.parser')
                    try :
                        blog_title = soup.find("span", {"class" : "pcol1 itemSubjectBoldfont"}).get_text().replace('\n','').strip()
                    except :
                        blog_title = soup.find("div", {"class" : "pcol1"}).get_text().replace('\n','').strip()
                        
                    blog_title = blog_title.encode('cp949','ignore')
                    blog_title = blog_title.decode('cp949','ignore')   
                    print(blog_title)
                    
                    try :
                        blog_date = soup.find("span", {"class" : "se_publishDate pcol2"}).get_text()
                    except :
                        blog_date = soup.find("p", {"class" : "date fil5 pcol2 _postAddDate"}).get_text()
                    print(blog_date)
                    try :
                        blog_writer = soup.find("div", {"class" : "nick"}).find("span", {"class": "itemfont col"}).get_text().strip('()')
                    except :
                        blog_writer = soup.find("strong", {"id" : "nickNameArea"}).get_text().strip()
                    print(blog_writer)
                     # 공감 버튼이 없으면 공감 수 0으로
                    if soup.find("div", {"class" : "area_sympathy pcol2"}) is None :
                        blog_like = 0
                    else :
                        blog_like = driver.find_elements_by_xpath("//em[@class='u_cnt _count']")[0].text
                    print(blog_like)
                    # 댓글 쓰기로 되어있으면 댓글 수 0으로
                    if soup.find("div", {"class" : "wrap_postcomment"}).find("i", {"class": "ico"}) is None or soup.find("div", {"class" : "wrap_postcomment"}).find("i", {"class": "ico"}).find('em') is None :
                        reply_count = 0
                    else :
                        reply_count = soup.find("div", {"class" : "wrap_postcomment"}).find("div", {"class": "area_comment pcol2"}).find('em').get_text().replace(" ","")
                    print(reply_count)
                    
                    if soup.find("div", {"id" : "postViewArea"}) is None :
                        if soup.find("div", {"class" : "se_component_wrap sect_dsc __se_component_area"}) is None :
                            blog_content = visible_texts(soup.find("div", {"class" : "se-main-container"})).replace('\n','').strip()
                        else :
                            blog_content = visible_texts(soup.find("div", {"class" : "se_component_wrap sect_dsc __se_component_area"})).replace('\n','').strip()
                    else :
                        blog_content = visible_texts(soup.find("div", {"id" : "postViewArea"})).replace('\n','').strip()
                    #인코딩
                    blog_content = blog_content.encode('cp949','ignore')
                    blog_content = blog_content.decode('cp949','ignore')
                    print(blog_content)
                    total_list.append([url,blog_title,blog_date,blog_writer,blog_like,reply_count,blog_content])

        driver.get(p_url)
        # 다음 페이지 버튼 있나 확인 후 없으면 while문 빠져나감
        try :
            driver.find_element_by_xpath("//a[@class='next']").click()
            page_num += 1
        except : 
            break;
            
     # 날짜 변환    
    dt_start_1 = dt_start_1 + day_1
    temp = str(dt_start_1)
    start_date = temp[:4]+temp[5:7]+temp[8:]
   
    save_DB()


# In[ ]:


# DB삭제시 이용
# query = """DROP DATABASE naver_blog; """
# curs.execute(query)


# In[ ]:


# DB내용 확인시 이용
# conn = pymysql.connect(host = "", user = "root", password = "", charset = "utf8")
# curs = conn.cursor()
# curs.execute("use naver_blog ;")
# query = """select * from 파이썬라이브러리; """
# curs.execute(query)
# all_rows = curs.fetchall()
# for i in all_rows:
#     print(i)

