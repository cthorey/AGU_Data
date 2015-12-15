import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
import pickle,time
from bs4 import BeautifulSoup
from tqdm import *

#racine = '/Users/thorey/Documents/MLearning/Side_Project/AGU_Data/'
racine = '/Users/clement/AGU_Data' 
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

def Scrapper(start,end,base_url):
    # Start the WebDriver and load the page           
    wd = webdriver.Firefox()
    papers = []
    errors = []
    first,last = start,end
    for idx in tqdm(range(start,end,2)):
        idx = str(idx)
        link = os.path.join(base_url,idx)
        wd.get(link)
        # Wait for the dynamically loaded elements to show up
        timeout = 30
        try:
            WebDriverWait(wd, timeout).until(
                EC.visibility_of_element_located((By.XPATH,'//*[@id="Content"]/section[1]')))  
            WebDriverWait(wd, timeout).until(
                EC.visibility_of_element_located((By.XPATH,'//*[@id="Details"]/section[1]')))
            WebDriverWait(wd, timeout).until(
                EC.visibility_of_element_located((By.XPATH,'//*[@id="Details"]/section[2]')))
            WebDriverWait(wd, timeout).until(
                EC.visibility_of_element_located((By.XPATH,'//*[@id="Details"]/section[3]')))
            time.sleep(3)
            body1 = wd.find_element_by_xpath('//*[@id="Content"]/section[1]').text
            body2 = wd.find_element_by_xpath('//*[@id="Details"]/section[1]').text
            body3 = wd.find_element_by_xpath('//*[@id="Details"]/section[2]').text
            body4 = wd.find_element_by_xpath('//*[@id="Details"]/section[3]').text
            paper = Paper(body1,body2,body3,body4,idx)
            papers.append(paper)
        except:
            errors.append(link)
            pass


    output = os.path.join(racine,'Data')
    name = os.path.join(output,'agu2015_'+str(start)+'_'+str(end))        
    with open(name, 'wb') as fi:
        pickle.dump({'papers':papers,'error':errors}, fi, pickle.HIGHEST_PROTOCOL)
    
    wd.quit()

def calc_end(end,base_end):
    if end > base_end:
        return base_end
    else:
        return end
    
def calc_start(base_start):
    done_papers = os.listdir(os.path.join(racine,'Data'))
    if len(done_papers)==0:
        return base_start
    else:
        return  max(map(int,[f.split('_')[2] for f in done_papers]))            

#####################
####### MAIN ########    
#####################
    
base_url = 'https://agu.confex.com/agu/fm15/meetingapp.cgi/Paper/'    
base_start = 58180
base_end = 87000

#What remains to do
step = 50 # Diviser par 2 pour avoir le nombre de paper a download
start = calc_start(base_start)
end = calc_end(start+step,base_end)

print 'We take back from paper %d'%(start)
bool_end = True
while bool_end:
    Scrapper(start,end,base_url)
    print 'Succesfully donwload papers from %d to %d'%(start,end)
    start = end
    end = calc_end(start+step,base_end)
    if end == base_end:
        bool_end = False
