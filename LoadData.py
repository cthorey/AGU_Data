import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
import pickle,time,datetime
from bs4 import BeautifulSoup
from tqdm import *

racine = '/Users/thorey/Documents/MLearning/Side_Project/AGU_Data/'
#racine = '/Users/clement/AGU_Data' 
year = 'agu2015'

class Paper(object):
    def __init__(self,wd,link):
        self.link = link
        wd.get(link)
        self.wait_for_elements(wd)
        self.tag = wd.find_element_by_class_name('itemTitle').text.split(':')[0]
        self.title = wd.find_element_by_class_name('itemTitle').text.split(':')[1]
        self.date = wd.find_element_by_class_name('SlotDate').text
        self.time = wd.find_element_by_class_name('SlotTime').text
        self.place = wd.find_element_by_class_name('propertyInfo').text
        self.abstract = wd.find_element_by_class_name('Additional').text.split('Reference')[0]
        try:
            self.reference = wd.find_element_by_class_name('Additional').text.split('Reference')[1]
        except:
            self.reference = ''
        self.authors = wd.find_element_by_class_name('PersonList').text
        self.session = wd.find_element_by_class_name('SessionListItem').text.split(':')[1]
        self.section = wd.find_element_by_class_name('infoBox').text.split("\n")[2].split(':')[-1]
        
        
    def wait_for_elements(self,wd,timeout = 15):
        classes = ['itemTitle','SlotDate','SlotTime','propertyInfo','Additional']
        classes += ['PersonList','SessionListItem','infoBox']
        for classe in classes:
            # wait for the different sections to download
            WebDriverWait(wd, timeout).until(EC.visibility_of_element_located((By.CLASS_NAME,classe)))
        time.sleep(3)
        
        
def Run_Scrapping(start,end,base_url):
    # Start the WebDriver and load the page           
    wd = webdriver.Chrome(os.path.join(racine,'chromedriver'))
    papers = []
    errors = []
    first,last = start,end
    progress = open(os.path.join(racine,year+'_progress.txt'),'w+')
    for idx in tqdm(range(start,end),file = progress):
        idx = str(idx)
        link = os.path.join(base_url,idx)
        try:
            papers.append(Paper(wd,link))
        except:
            errors.append(link)
    wd.quit()
    progress.close()            
    return {'papers':papers,'error':errors}
        
def Pickler(obj):
    output = os.path.join(racine,'Data')
    name = os.path.join(output,year+'_'+str(start)+'_'+str(end))        
    with open(name, 'wb') as fi:
        pickle.dump({'papers':papers,'error':errors}, fi, pickle.HIGHEST_PROTOCOL)

    
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


if __name__ == "__main__":        
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
    step = 10
    start = calc_start(base_start,year)
    end = calc_end(start+step,base_end)

    bilan = open(os.path.join(racine,year+'_bilan.txt'),'a')
    bilan.write('hello, we are processing %s \n'%(year))
    bilan.write('Scrapping commencer le %s \n'%(str(datetime.date.today())))
    bilan.write('We take back from paper %d \n'%(start))
    bilan.close()

    bool_end = True
    while bool_end:
        data = Run_Scrapping(start,end,base_url)
        Pickler(data)
        bilan = open(os.path.join(racine,year+'_bilan.txt'),'a')
        bilan.write('Succesfully donwload papers from %d to %d \n'%(start,end))
        bilan.close()
        start = end
        end = calc_end(start+step,base_end)
        if end == base_end:
            bool_end = False

