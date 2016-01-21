######## IMPORT    #########
import json
import codecs
import os
import time
from tqdm import *
from os.path import expanduser
import pandas as pd
import unicodedata

######## PARAMETER #########
home = expanduser("~")
racine = os.path.join(home, 'Documents', 'repos', 'agu_data', 'agu_data')
year = 'agu2014'

COUNTRY = pd.read_csv(os.path.join(racine, 'Data', 'country.csv'))
COUNTRY.value = map(lambda x: x.lower(), COUNTRY.value)

###### FUNCTIONS #########


def load_json(name):
    with codecs.open(name, 'r', 'utf8') as f:
        return json.load(f)

##### PAPERS ########


class Paper(object):
    ''' handle each paper submitted to AGU data base '''

    def __init__(self, link, data):
        self.link = link
        for key, val in data.iteritems():
            setattr(self, key, val)


def get_all_data(year):
    ''' Go looking for all the files and load it as a list of
    Paper object '''

    name = os.listdir(os.path.join(racine, 'Data', year))
    name = [f for f in name if f.split('_')[-1] == 'V3.json']
    papers = []
    for json in tqdm(name):
        json_file = os.path.join(racine, 'Data', year, json)
        papers += [Paper(key, val) for key, val
                   in load_json(json_file)['papers'].iteritems()]

    return papers

    #### Contributors #####


class Contributor(object):
    '''
    Handle each contributor

    '''

    def __init__(self, link, data):
        self.link = link
        for key, val in data.iteritems():
            setattr(self, key, val)
        try:
            country = COUNTRY.value
            ad = self._clean_unicode(self.address.replace('\n', ' ')).lower()
            self.country = country[
                map(lambda x: x in str(ad), country).index(True)]
        except:
            self.country = ''

    def _clean_unicode(self, x):
        return unicodedata.normalize('NFKD', x).encode('ascii', 'ignore')


def get_all_contrib(year):
    ''' Go looking for all the files and load it as a list of
    Paper object '''

    names = os.listdir(os.path.join(racine, 'Data', year))
    names = [f for f in names if f.split(
        '_')[-1] == 'V1.json' and f.split('_')[0] == 'Name']
    contributors = []

    for json in tqdm(names):
        json_file = os.path.join(racine, 'Data', year, json)
        contributors += [Contributor(key, val) for key, val
                         in load_json(json_file)['names'].iteritems()]

    return contributors
