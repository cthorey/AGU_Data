import os
import sys
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
racine = os.path.join(home, 'Documents', 'project',
                      'agu_data', 'repo', 'agu_data')


def wait_for_elements(wd, classes, timeout=2):
    ''' Wait for elements to appear on the page

    Args:
        wd : selenium web driver
        timeout (Optionnal[int]): Number of seconds to wait
        before the timeout.
        classes : classes name balise to wait for

    Note:
        Since 2014, the agu website mainly calls javascript to fill up
        the content of different papers. The webdriver needs to wait
        for these element to appear on the page before it can get them.

    '''

    for classe in classes:
        # wait for the different sections to download
        try:
            WebDriverWait(wd, timeout).until(
                EC.visibility_of_element_located((By.CLASS_NAME, classe)))
        except:
            time.sleep(6)


def Scrap_page(wd, link):
    '''Scrapping of the page to gather the name, the institute, the
    country, the number of session involved (chair, converniers..) and
    the number of papers affilitated.

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
    data = {}
    wait_for_elements(wd, ['AddressList'])
    data.update({'name':
                 wd.find_element_by_class_name('itemTitle').text})
    data.update({'address':
                 wd.find_element_by_class_name('AddressList').text})
    wait_for_elements(wd, ['SessionListItem', 'PaperListItem'])
    data.update({'name':
                 wd.find_element_by_class_name('itemTitle').text})
    data.update({'address':
                 wd.find_element_by_class_name('AddressList').text})
    data.update({'session': {f.text.split(' ')[0]: ' '.join(f.text.split(' ')[1:])
                             for f
                             in wd.find_elements_by_class_name('SessionListItem')}})
    data.update({'papers': {f.text.split(' ')[0]: ' '.join(f.text.split(' ')[1:])
                            for f in
                            wd.find_elements_by_class_name('PaperListItem')}})
    return data


def Run_Scrapping(start, end, base_url):
    ''' Start the scrapping of all names for one specific
    agu.

    Note:
        Since 2014, the agu website mainly calls javascript to fill up
        the content of different page. It is organized with a base_url
        that usually ends by Paper/ followed by a sequence of integer, each
        integer corresponding to one paper. While I didn't really get how the
        range of integers is decided, it looks like to be all integers between
        58000 and 87000 for 2015. In2014, it was more like between 2180
        and 35000

    Args:
        start (int): Starting paper
        end (int): Ending paper
        base_url: Url where the names are stored.

    Returns:
        A dictionnary with a key *names* containing itself a list of
        dictionnary, one for each name that we manage to scrape.
        The second key *error* corresponds to all the papers that we failed
        to scrap.

    Note:
        Each succesfull scrapped name is ordered also as a dictionary to
        easily store them a .json files.

    Example:
        For the year 2015,

        >>> base_url = 'https://agu.confex.com/agu/fm15/meetingapp.cgi/Paper/'
        >>> Run_Scrapping(58000,87000,base_url)

        looks to scrap almost all the names.

    '''
    wd = webdriver.Chrome(os.path.join(racine, 'chromedriver'))
    names = {}
    errors = []
    first, last = start, end
    progressfile = os.path.join(
        racine, year + '_progress_' + str(start) + '_' + str(end) + '.txt')
    progress = open(progressfile, 'w+')
    for idx in tqdm(range(start, end), file=progress):
        idx = str(idx)
        link = os.path.join(base_url, idx)
        try:
            names.update({link: Scrap_page(wd, link)})
        except:
            errors.append(link)
    wd.quit()
    progress.close()
    return {'names': names, 'error': errors}


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
    ''' Run the scrapping

    syntax : python Scrap_names.py year base_start base_end step
    '''
    if len(sys.argv) != 5:
        raise ValueError('Acceptable syntax: \n' +
                         'python Scrap_names.py year base_start base_end step')

    if int(sys.argv[1]) not in [2014, 2015]:
        raise ValueError('Either provide 2014 or 2015 as a 2nd argument')
    else:
        print 'Let scrap AGU data from %s' % (str(sys.argv[1]))
    year = 'agu' + str(sys.argv[1])

    base_url = 'https://agu.confex.com/agu/fm' + str(sys.argv[1])[-2:] \
               + '/meetingapp.cgi/Person/'
    base_start = int(sys.argv[2])
    base_end = int(sys.argv[3])
    step = int(sys.argv[4])

    isdirok(year)

    # What remains to do
    start = calc_start(base_start, year)
    end = calc_end(start + step, base_end)

    bilanfile = os.path.join(racine, year +
                             '_bilan' + str(base_start) + '_' +
                             str(base_end) + '.txt')
    bilan = open(bilanfile, 'a')
    bilan.write('hello, we are processing %s \n' % (year))
    bilan.write('Scrapping commencer le %s \n' % (str(datetime.date.today())))
    bilan.write('We take back from paper %d until %d\n' %
                (base_start, base_end))
    bilan.close()

    bool_end = True
    while bool_end:
        if end == base_end:
            bool_end = False
        data = Run_Scrapping(start, end, base_url)
        name = 'Name_' + str(start) + '_' + str(end) + '_V1'
        Jsoner(data, year, name)
        bilan = open(bilanfile, 'a')
        bilan.write('Succesfully donwload papers from %d to %d \n' %
                    (start, end))
        bilan.close()
        start = end
        end = calc_end(start + step, base_end)
