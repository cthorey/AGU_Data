import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
import pickle,time
from bs4 import BeautifulSoup


class Paper(object):
    ''' Class to handle each paper on the website AGU'''
    def __init__(self,body1,body2,body3,body4,idx):
        self.tag_session = body1.split(':')[0]
        self.title =  body1.split(':')[1]
        self.abstract = body2.split('Reference')[0]
        try:
            self.reference = body2.split('Reference')[1]
        except:
            self.reference = ''
        self.author = body3.split('\n')[1:]
        self.session = str(body4.split('\n')[1].split(':')[1])
        self.focus_group = str(body4.split('\n')[2].split(':')[1])
        self.date = str(body4.split('\n')[3].split(':')[1])
        self.idx = idx

# Start the WebDriver and load the page           
wd = webdriver.Firefox()
base_url = 'https://agu.confex.com/agu/fm15/meetingapp.cgi/Paper/'

papers = []
errors = []
first,last = 58180 , 87000
incr = 0
for idx in map(str,range(70012,70052,2)):
    link = os.path.join(base_url,idx)
    print link
    wd.get(link)
    # Wait for the dynamically loaded elements to show up
    WebDriverWait(wd, 60).until(
        EC.visibility_of_element_located((By.XPATH,'//*[@id="Content"]/section[1]')))  
    WebDriverWait(wd, 60).until(
        EC.visibility_of_element_located((By.XPATH,'//*[@id="Details"]/section[1]')))
    WebDriverWait(wd, 60).until(
        EC.visibility_of_element_located((By.XPATH,'//*[@id="Details"]/section[2]')))
    WebDriverWait(wd, 60).until(
        EC.visibility_of_element_located((By.XPATH,'//*[@id="Details"]/section[3]')))
    time.sleep(3)
    body1 = wd.find_element_by_xpath('//*[@id="Content"]/section[1]').text
    body2 = wd.find_element_by_xpath('//*[@id="Details"]/section[1]').text
    body3 = wd.find_element_by_xpath('//*[@id="Details"]/section[2]').text
    body4 = wd.find_element_by_xpath('//*[@id="Details"]/section[3]').text
    try:
        paper = Paper(body1,body2,body3,body4,idx)
        papers.append(paper)
    except:
        errors.append(link)
        pass


output = '/Users/thorey/Documents/MLearning/Side_Project/AGU_Data/Data'
name = os.path.join(output,'agu2015')        
with open(name, 'wb') as fi:
    pickle.dump({'papers':papers,'error':errors}, fi, pickle.HIGHEST_PROTOCOL)
    
wd.quit()
