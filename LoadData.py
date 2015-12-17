import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
import pickle,time,datetime
from bs4 import BeautifulSoup
from tqdm import *

#racine = '/Users/thorey/Documents/MLearning/Side_Project/AGU_Data/'
racine = '/Users/clement/AGU_Data' 
year = 'agu2014'

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
    progress = open(os.path.join(racine,year+'_progress.txt'),'w+')
    for idx in tqdm(range(start,end),file = progress):
        idx = str(idx)
        link = os.path.join(base_url,idx)
        wd.get(link)
        # Wait for the dynamically loaded elements to show up
        timeout = 20
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
    name = os.path.join(output,year+'_'+str(start)+'_'+str(end))        
    with open(name, 'wb') as fi:
        pickle.dump({'papers':papers,'error':errors}, fi, pickle.HIGHEST_PROTOCOL)
    
    wd.quit()
    progress.close()
    
def calc_end(end,base_end):
    if end > base_end:
        return base_end
    else:
        return end
    
def calc_start(base_start,year):
    done_papers = os.listdir(os.path.join(racine,'Data'))
    done_papers = [f for f in done_papers if f.split('_')[0] == year]
    if len(done_papers) == 0:
        return base_start
    else:
        return  max(map(int,[f.split('_')[2] for f in done_papers]))            

#####################
####### MAIN ########    
#####################

if year.split('agu')[-1] == '2015':
    base_url = 'https://agu.confex.com/agu/fm15/meetingapp.cgi/Paper/'    
    base_start = 58180
    base_end = 87000
elif year.split('agu')[-1] == '2014':
    base_url = 'https://agu.confex.com/agu/fm14/meetingapp.cgi/Paper/'    
    base_start = 2180
    base_end = 35000
else:
    print 'Error base_url : %s'%(base_url)
    raise Exception
    
#What remains to do
step = 1000 
start = calc_start(base_start,year)
end = calc_end(start+step,base_end)

bilan = open(os.path.join(racine,year+'_bilan.txt'),'a')
bilan.write('hello, we are processing %s \n'%(year))
bilan.write('Scrapping commencer le %s \n'%(str(datetime.date.today())))
bilan.write('We take back from paper %d \n'%(start))
bilan.close()

bool_end = True
while bool_end:
    Scrapper(start,end,base_url)
    bilan = open(os.path.join(racine,year+'_bilan.txt'),'a')
    bilan.write('Succesfully donwload papers from %d to %d \n'%(start,end))
    bilan.close()
    start = end
    end = calc_end(start+step,base_end)
    if end == base_end:
        bool_end = False

