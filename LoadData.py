import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
import time,datetime
import codecs, json
from bs4 import BeautifulSoup
from tqdm import *
        
def wait_for_elements(wd,timeout = 15):
    classes = ['itemTitle','SlotDate','SlotTime','propertyInfo','Additional']
    classes += ['PersonList','SessionListItem','infoBox']
    for classe in classes:
        # wait for the different sections to download
        WebDriverWait(wd, timeout).until(EC.visibility_of_element_located((By.CLASS_NAME,classe)))
    time.sleep(3)
        
def Scrap_page(wd,link):
    wd.get(link)
    wait_for_elements(wd)
    data = {}
    data.update({'tag' :
                 wd.find_element_by_class_name('itemTitle').text.split(':')[0]})
    data.update({'title' :
                 wd.find_element_by_class_name('itemTitle').text.split(':')[1]})
    data.update({'date' :
                 wd.find_element_by_class_name('SlotDate').text})
    data.update({'time' :
                 wd.find_element_by_class_name('SlotTime').text})
    data.update({'place' :
                 wd.find_element_by_class_name('propertyInfo').text})
    data.update({'abstract' :
                 wd.find_element_by_class_name('Additional').text.split('Reference')[0]})
    try:
        data.update({'reference' :
                     wd.find_element_by_class_name('Additional').text.split('Reference')[1]})
    except:
        data.update({'reference' : '' })
    authors = wd.find_elements_by_class_name('RoleListItem')
    data.update({'authors' :
                 {author.text.split('\n')[0] : ', '.join(author.text.split('\n')[1:])
                  for author in authors}})
    data.update({'session' :
                 wd.find_element_by_class_name('SessionListItem').text.split(':')[1]})    
    data.update({'section' :
                 wd.find_element_by_class_name('infoBox').text.split("\n")[2].split(':')[-1]})        
    return data
        
def Run_Scrapping(start,end,base_url):
    # Start the WebDriver and load the page           
    wd = webdriver.Chrome(os.path.join(racine,'chromedriver'))
    papers = {}
    errors = []
    first,last = start,end
    progress = open(os.path.join(racine,year+'_progress.txt'),'w+')
    for idx in tqdm(range(start,end),file = progress):
        idx = str(idx)
        link = os.path.join(base_url,idx)
        try:
            papers.update({link:Scrap_page(wd,link)})
        except:
            errors.append(link)
    wd.quit()
    progress.close()            
    return {'papers':papers,'error':errors}
        
def Jsoner(data,year,name):
    name_json = os.path.join(racine,'Data',year,name)
    with codecs.open(name_json+'.json', 'w+', 'utf8') as outfile:
        json.dump(data,
                  outfile,
                  sort_keys = True,
                  indent = 4,
                  ensure_ascii=False)

def isdirok(year):
    output = os.path.join(racine,'Data')
    if not os.path.isdir(os.path.join(output,year)):
        os.mkdir(os.path.join(output,year))
        
def calc_end(end,base_end):
    if end > base_end:
        return base_end
    else:
        return end
    
def calc_start(base_start,year):
    done_papers = os.listdir(os.path.join(racine,'Data',year))
    done_papers = [f for f in done_papers
                   if (len(f.split('_')) == 2) and (f[0] != '.') and (f.split('_')[-1] == 'V2.json') ]
    print done_papers
    if len(done_papers) == 0:
        print base_start
        return base_start
    else:
        print max(map(int,[f.split('_')[1] for f in done_papers]))            
        return  max(map(int,[f.split('_')[1] for f in done_papers]))            


if __name__ == "__main__":        
    #####################
    ####### MAIN ########    
    #####################
    
    racine = '/Users/thorey/Documents/MLearning/Side_Project/AGU_Data/'
    #racine = '/Users/clement/AGU_Data' 
    year = 'agu2015'
    step = 50
    isdirok(year)
    
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
        name = str(start)+'_'+str(end)+'_V2'
        Jsoner(data,year,name)
        bilan = open(os.path.join(racine,year+'_bilan.txt'),'a')
        bilan.write('Succesfully donwload papers from %d to %d \n'%(start,end))
        bilan.close()
        start = end
        end = calc_end(start+step,base_end)
        if end == base_end:
            bool_end = False
            
