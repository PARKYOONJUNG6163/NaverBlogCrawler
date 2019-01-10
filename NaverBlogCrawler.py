
# coding: utf-8

# In[1]:


from selenium import webdriver
from selenium.webdriver.common.keys import Keys

from bs4 import BeautifulSoup

import datetime 
import pymysql


# In[2]:


def save_DB() : 
    conn = pymysql.connect(host = "147.43.122.34", user = "root", password = "1234", charset = "utf8")
    curs = conn.cursor()
    
    curs.execute("use naver_blog ;")

    query = """CREATE TABLE IF NOT EXISTS """+ keyword+ """(ID int, URL varchar(100), Title varchar(100), Date varchar(20), Writer varchar(50), blog_like int, Count int,Text text(62200));"""
    curs.execute(query)

    query = """ALTER TABLE """ + keyword +""" CHARACTER SET utf8 COLLATE utf8_general_ci;"""
    curs.execute(query)

    conn.commit()
    
    select_query = """SELECT * from """ + keyword 
    index = curs.execute(select_query)

    for value in total_list :
        url = value[0]
        title = value[1]
        date = value[2]
        writer = value[3]
        like = value[4]
        count = value[5]
        content = value[6]

        query = """insert into """ + keyword + """(ID, URL, Title, Date, Writer, blog_like, Count, Text) values (%s, %s, %s, %s, %s, %s, %s, %s) ; """
        curs.execute(query, (str(index), url, title, date,writer,like,count,content))

        index = index + 1 

        conn.commit()
        
    conn.close()
    print("FINISH")


# In[3]:


keyword = input("Keyword ? ")

start_year = input("Start Year ? ")
start_month = input("Start Month ? ")
start_day = input("Start Day ? ")

end_year = input("End Year ? ")
end_month = input("End Month ? ")
end_day = input("End Day ? ")

start_date = start_year+start_month+start_day
end_date = end_year+end_month+end_day


# In[4]:


options = webdriver.ChromeOptions()
options.add_argument('headless')
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
        driver = webdriver.Chrome('./chromedriver/chromedriver',chrome_options=options)
        driver.implicitly_wait(3)
        driver.get(p_url)
        soup = BeautifulSoup(driver.page_source,'html.parser')

        dd_tags = driver.find_elements_by_class_name('txt_inline')
        a_tags = soup.select('ul#elThumbnailResultArea li dl dt a')

        # 한 페이지에 있는 링크들 전부 가져오기
        for a,d in zip(a_tags,dd_tags) :
            if 'href' in a.attrs :
                if 'blog.me' in a.attrs['href'] or 'blog.naver.com' in a.attrs['href'] :
                    url = a.attrs['href']
                    driver = webdriver.Chrome('./chromedriver/chromedriver',chrome_options=options)
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

                    blog_title = driver.find_element_by_class_name('pcol1').text.replace('\n','')

                    blog_date = d.text
                    
                    blog_writer = soup.find("div", {"class" : "nick"}).find("span", {"class": "itemfont col"}).text.strip('()')
                    
                     # 공감 버튼이 없으면 공감 수 0으로
                    if soup.find("div", {"class" : "area_sympathy pcol2"}) is None :
                        blog_like = 0
                    else :
                        blog_like = driver.find_elements_by_xpath("//em[@class='u_cnt _count']")[0].text

                    # 댓글 쓰기로 되어있으면 댓글 수 0으로
                    if soup.find("div", {"class" : "wrap_postcomment"}).find("i", {"class": "ico"}) is None or soup.find("div", {"class" : "wrap_postcomment"}).find("i", {"class": "ico"}).find('em') is None :
                        reply_count = 0
                    else :
                        reply_count = soup.find("div", {"class" : "wrap_postcomment"}).find("div", {"class": "area_comment pcol2"}).find('em').text.replace(" ","")

                    if soup.find("div", {"id" : "postViewArea"}) is None :
                        if soup.find("div", {"class" : "se_component_wrap sect_dsc __se_component_area"}) is None :
                            blog_content = soup.find("div", {"class" : "se-main-container"}).text.replace('\n','')
                        else :
                            blog_content = soup.find("div", {"class" : "se_component_wrap sect_dsc __se_component_area"}).text.replace('\n','')
                    else :
                        blog_content = soup.find("div", {"id" : "postViewArea"}).text.replace('\n','').strip()

                    total_list.append([url,blog_title,blog_date,blog_writer,blog_like,reply_count,blog_content])

        driver.get(p_url)
        page_num += 1
        # 다음 페이지 버튼 있나 확인 후 없으면 while문 빠져나감
        try :
            driver.find_element_by_xpath("//a[@class='next']").click()
        except : 
            break;
            
     # 날짜 변환    
    dt_start_1 = dt_start_1 + day_1
    temp = str(dt_start_1)
    start_date = temp[:4]+temp[5:7]+temp[8:]
   
    save_DB()


# In[7]:


# DB 생성시 이용
# query = """CREATE DATABASE naver_blog default CHARACTER SET UTF8;"""
# curs.execute(query)


# In[6]:


# DB삭제시 이용
# query = """DROP DATABASE naver_blog; """
# curs.execute(query)


# In[5]:


# DB내용 확인시 이용
# conn = pymysql.connect(host = "147.43.122.34", user = "root", password = "1234", charset = "utf8")
# curs = conn.cursor()
# curs.execute("use naver_blog ;")
# query = """select * from 파이썬라이브러리; """
# curs.execute(query)
# all_rows = curs.fetchall()
# for i in all_rows:
#     print(i)

