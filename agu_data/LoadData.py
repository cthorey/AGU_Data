""" Module to ease the scrap of the `AGU website`_

This module ease the scrapping of the abstract form the `AGU website`_
for the year 2014 and 2015. Before this date, the program was only
available as a pdf file.

Example:
    For instance, if I wan to scrap all the abstract for 2015
    2015 `AGU website`_, I just have to run::

        $ python LoadData.py

    and be patient as this may take some time ;)

Attributes:
    HOME (str): Home folder your computer. 
    racine (str): Racine of the working directory. When run,
    the program is going to create a directory 'Data' to store
    the json file containing the results of the scrapping.
    year (str): Either 'agu2015' or 'agu2014'

.. _AGU website:
   https://agu.confex.com/agu/fm15/meetingapp.cgi

"""

import os
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium import webdriver
import time
import datetime
import codecs
import json
from bs4 import BeautifulSoup
from tqdm import *
from os.path import expanduser

home = expanduser("~")
racine = os.path.join(home, 'Documents', 'repos', 'agu_data', 'agu_data')
year = 'agu2014'


def wait_for_elements(wd, timeout=15):
    ''' Wait for elements to appear on the page

    Args:
        wd : selenium web driver
        timeout (Optionnal[int]): Number of seconds to wait
        before the timeout.

    Note:
        Since 2014, the agu website mainly calls javascript to fill up
        the content of different papers. The webdriver needs to wait
        for these element to appear on the page before it can get them.

    '''
    classes = ['itemTitle', 'SlotDate',
               'SlotTime', 'propertyInfo', 'Additional']
    classes += ['PersonList', 'SessionListItem', 'infoBox']
    for classe in classes:
        # wait for the different sections to download
        WebDriverWait(wd, timeout).until(
            EC.visibility_of_element_located((By.CLASS_NAME, classe)))
    time.sleep(3)


def Scrap_page(wd, link):
    ''' Scrapping of the page

    Args:
        wd: selenium web driver
        link (str): link to go scrap

    Returns:
        A dictionnary which contains information about
        the paper which is contained in link. In particular,
        the scrapper collects information about tag, title, date,
        time, place, abstract, reference, authors, session, section.

    Note:
        It is very easy to identify element by either tag, or class name.
        Juste open a browser and toggle inspect element. It gives you
        the html code with the according balise.

    Warning:
        Their is no tag in the title in AGU 2014 !!
    '''
    wd.get(link)
    wait_for_elements(wd)
    data = {}
    if year == 'agu2015':
        data.update({'tag':
                     wd.find_element_by_class_name('itemTitle').text.split(':')[0]})
        data.update({'title':
                     wd.find_element_by_class_name('itemTitle').text.split(':')[1:]})
    elif year == 'agu2014':
        data.update({'title':
                     wd.find_element_by_class_name('itemTitle').text})
    data.update({'date':
                 wd.find_element_by_class_name('SlotDate').text})
    data.update({'time':
                 wd.find_element_by_class_name('SlotTime').text})
    data.update({'place':
                 wd.find_element_by_class_name('propertyInfo').text})
    data.update({'abstract':
                 wd.find_element_by_class_name('Additional').text.split('Reference')[0]})
    try:
        data.update({'reference':
                     wd.find_element_by_class_name('Additional').text.split('Reference')[1]})
    except:
        data.update({'reference': ''})
    authors = wd.find_elements_by_class_name('RoleListItem')
    data.update({'authors':
                 {author.text.split('\n')[0]: ', '.join(author.text.split('\n')[1:])
                  for author in authors}})
    data.update({'session':
                 wd.find_element_by_class_name('SessionListItem').text.split(':')[1]})
    data.update({'section':
                 wd.find_element_by_class_name('infoBox').text.split("\n")[2].split(':')[-1]})
    return data


def Run_Scrapping(start, end, base_url):
    ''' Start the scrapping of all papers for one specific
    agu.

    Note:
        Since 2014, the agu website mainly calls javascript to fill up
        the content of different papers. It is organized with a base_url
        that usually ends by Paper/ followed by a sequence of integer, each
        integer corresponding to one paper. While I didn't really get how the
        range of integers is decided, it looks like to be all integers between
        58000 and 87000 for 2015. In2014, it was more like between 2180
        and 35000

    Args:
        start (int): Starting paper
        end (int): Ending paper
        base_url: Url where the papers are stored.

    Returns:
        A dictionnary with a key *papers* containing itself a list of
        dictionnary, one for each paper that we manage to scrape.
        The second key *error* corresponds to all the papers that we failed
        to scrap.

    Note:
        Each succesfull scrapped paper is ordered also as a dictionary to
        easily store them a .json files.

    Example:
        For the year 2015,

        >>> base_url = 'https://agu.confex.com/agu/fm15/meetingapp.cgi/Paper/'
        >>> Run_Scrapping(58000,87000,base_url)

        looks to scrap almost all the papers. 

    '''
    wd = webdriver.Chrome(os.path.join(racine, 'chromedriver'))
    papers = {}
    errors = []
    first, last = start, end
    progress = open(os.path.join(racine, year + '_progress.txt'), 'w+')
    for idx in tqdm(range(start, end), file=progress):
        idx = str(idx)
        link = os.path.join(base_url, idx)
        try:
            papers.update({link: Scrap_page(wd, link)})
        except:
            errors.append(link)
    wd.quit()
    progress.close()
    return {'papers': papers, 'error': errors}


def Jsoner(data, year, name):
    ''' Store the results from the scrapping as a .json file

    Args:
        data (dict): A dictionary containing the result of run_scrapping
        year (str): The year considered 
        name (str): Name of the .json file

    '''
    name_json = os.path.join(racine, 'Data', str(year), name)
    with codecs.open(name_json + '.json', 'w+', 'utf8') as outfile:
        json.dump(data,
                  outfile,
                  sort_keys=True,
                  indent=4,
                  ensure_ascii=False)


def isdirok(year):
    ''' Ensure the directory exist before scrapping

    Args:
        year (str): directory where the json file are going to
        be stored

    '''

    output = os.path.join(racine, 'Data')
    if not os.path.isdir(output):
        os.mkdir(output)
    if not os.path.isdir(os.path.join(output, year)):
        os.mkdir(os.path.join(output, year))


def calc_end(end, base_end):
    ''' Ensure the ending integer not larger than the bounds

    Args: 
        end (int): Proposed ending integer
        base_end (int): Maximum integer value.

    Note:
        It is advised to run the scrapping step by step, i.e.
        1000 papers by 1000 and then store json file each
        1000 papers. This function decide if the upper bound for
        the next scrapping does not depass the maximum.

    '''

    if end > base_end:
        return base_end
    else:
        return end


def calc_start(base_start, year):
    '''Calc beginning integer according to what's already done

    Args: 
        base_start (int): Minimum integer of the sequence
        year (int): Year that your want to scrape

    Note:
        It is advised to run the scrapping step by step, i.e.  1000
        papers by 1000 and then store json file each 1000 papers. This
        function decide if the lower bound for the next scrapping is
        in agreement with the minimum.

    '''
    done_papers = os.listdir(os.path.join(racine, 'Data', year))
    done_papers = [f for f in done_papers
                   if (len(f.split('_')) == 3) and (f[0] != '.') and (f.split('_')[-1] == 'V2.json')]
    print done_papers
    if len(done_papers) == 0:
        print base_start
        return base_start
    else:
        print max(map(int, [f.split('_')[1] for f in done_papers]))
        return max(map(int, [f.split('_')[1] for f in done_papers]))


if __name__ == "__main__":
    ''' Run the scrapping '''

    step = 1000

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
        print 'Error base_url : %s' % (base_url)
        raise Exception

    # What remains to do
    start = calc_start(base_start, year)
    end = calc_end(start + step, base_end)

    bilan = open(os.path.join(racine, year + '_bilan.txt'), 'a')
    bilan.write('hello, we are processing %s \n' % (year))
    bilan.write('Scrapping commencer le %s \n' % (str(datetime.date.today())))
    bilan.write('We take back from paper %d \n' % (start))
    bilan.close()

    bool_end = True
    while bool_end:
        data = Run_Scrapping(start, end, base_url)
        name = str(start) + '_' + str(end) + '_V3'
        Jsoner(data, year, name)
        bilan = open(os.path.join(racine, year + '_bilan.txt'), 'a')
        bilan.write('Succesfully donwload papers from %d to %d \n' %
                    (start, end))
        bilan.close()
        start = end
        end = calc_end(start + step, base_end)
        if end == base_end:
            bool_end = False
