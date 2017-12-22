#-*- coding=utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import urllib2
import sys
import codecs
import time
import random
import os

# company info class
class Company:
    #init
    def __init__(self, name="", job="", salary="", href = "", location = "", education = "", exp = "", discription=""):
        self.name = name
        self.job = job
        self.salary = salary
        self.href = href
        self.location = location
        self.education = education
        self.exp = exp
        self.discription = discription
        
    def to_string():
        print("hello ...")

    def set_discription(self, discription):
        self.discription = discription

def job_spider(url, key, companys):
    #init browser
    chromedriver = '/Users/zhengdf/wkdir/python3/build/mac/bin/chromedriver'
    os.environ["webdriver.chrome.driver"] = chromedriver
    driver = webdriver.Chrome(chromedriver)    
    driver.get(url + key)
    target_path = '//*[@id="sojob"]/div[2]/div/div[1]/div[1]/ul/li'
    wait_second = 10    
    WebDriverWait(driver, wait_second).until( EC.presence_of_element_located((By.XPATH, target_path )))
    elems = driver.find_elements_by_xpath( target_path )
    for elem in elems:
        target_path = './div/div[1]/h3/a'
        job_item = elem.find_element_by_xpath( target_path )
        job = job_item.text
        href = job_item.get_attribute('href')
        target_path = './div/div[1]/p[1]/span[1]'
        salary_item = elem.find_element_by_xpath( target_path )
        salary = salary_item.text
        target_path = './div/div[2]/p[1]/a'
        name_item = elem.find_element_by_xpath( target_path )
        name = name_item.text
        local = elem.find_element_by_xpath('./div/div[1]/p[1]/a').text
        education = elem.find_element_by_xpath('./div/div[1]/p[1]/span[2]').text
        exp = elem.find_element_by_xpath('./div/div[1]/p[1]/span[3]').text
        companys.append(Company(name, job, salary, href, local, education, exp))
    #get dicription
    for company in companys:
        print("company %s ..." % company.name)
        url = company.href
        driver.get(url)
        target_path = '//*[@id="job-view-enterprise"]/div[1]/div[1]/div[1]/div[1]/div[3]/div'
        wait_second = 10    
        WebDriverWait(driver, wait_second).until( EC.presence_of_element_located((By.XPATH, target_path )))
        elem = driver.find_element_by_xpath( target_path )
        company.set_discription(elem.text.replace("\n", " ").replace(",", "."))
    #quit
    driver.quit()

#def analize
from wordcloud import WordCloud
import jieba
import PIL
import matplotlib.pyplot as plt
import numpy as np

def nanalize_job(companys, key):
    text = ""
    for company in companys:
        text += company.discription

    words = jieba.cut(text)
    a = []
    for word in words:
        if len(word) > 1:
            a.append(word)
    text=r' '.join(a)
    font_path = u'./font/msyh.ttf'
    wordcloud = WordCloud(font_path, background_color="white",   
                          margin=5, width=1800, height=800)
    wordcloud = wordcloud.generate(text)
    filename = "./images/" + key + "-wordcloud.jpg"
    wordcloud.to_file(filename)

    #salary counter
    # <10w 10-15 15-20 20-25 >25
    calc = [0, 0, 0, 0, 0, 0]
    for company in companys:
        salary = company.salary[0:-1].split('-')
        if len(salary) == 1:
            calc[5] += 1
        elif int(salary[1]) <= 10:
            calc[0] += 1
        elif int(salary[1]) > 10 and int(salary[1]) < 15:
            calc[1] += 1
        elif int(salary[1]) >= 15 and int(salary[1]) < 20:
            calc[2] += 1
        elif int(salary[1]) >= 20 and int(salary[1]) < 25:
            calc[3] += 1
        elif int(salary[1]) >= 25:
            calc[4] += 1
    plt.title(u"salary")
    plt.xlabel(u'Annual salary')
    plt.ylabel(u'counts')
    axis = ["<10w", "10-15w", "15-20w", "20-25w", ">25w", "discuss"]
    x = range(len(axis))
    plt.plot(x, calc, 'ro-')
    plt.xticks(x, axis, rotation=0)
    plt.margins(0.08)
    plt.subplots_adjust(bottom=0.15)
    plt.savefig('./images/' + key + '-salary.jpg')
        
def write_to_file(companys, filename):
    file_object = codecs.open( filename, 'w', 'utf-8')
    file_object.write( "COMPANY, JOB, SALARY, LOCALTION, EDUCATION, EXP, DISCRIPTION\n" )
    for company in companys:
        file_object.write( "%s, %s, %s, %s, %s, %s, %s\n" % (company.name, company.job, company.salary, company.location, company.education, company.exp, company.discription))
        
def main(key):
    url = 'https://www.liepin.com/zhaopin/?industries=&dqs=270020&salary=&jobKind=&pubTime=&compkind=&compscale=&industryType=&searchType=1&clean_condition=&isAnalysis=&init=1&sortFlag=15&flushckid=1&fromSearchBtn=2&headckid=1e36a078aaab99b5&d_headId=170f56d51061a84fab65efaa3b648208&d_ckId=170f56d51061a84fab65efaa3b648208&d_sfrom=search_fp_bar&d_curPage=0&d_pageSize=40&siTag=I-7rQ0e90mv8a37po7dV3Q~fA9rXquZc5IkJpXC-Ycixw&key='
    companys = []
    job_spider(url, key, companys)
    out_filename = "./data/" + key + "-job-" + time.strftime("%Y-%m-%d", time.localtime())  + ".csv"
    write_to_file(companys, out_filename)
    nanalize_job(companys, key)

def usage() :
    print "usage : "
    print "     python liepin_spider.py key"

    
if __name__ == '__main__':
    if len(sys.argv) != 2 :
        usage()
        exit()
    key = sys.argv[1]
    main(key)
