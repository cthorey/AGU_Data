######## IMPORT    #########
import json
import codecs
import os
import time
from tqdm import *
from os.path import expanduser
import pandas as pd
import unicodedata
import pycountry

######## PARAMETER #########
home = expanduser("~")
racine = os.path.join(home, 'Documents', 'project',
                      'agu_data', 'repo', 'agu_data')
year = 'agu2014'

###### FUNCTIONS #########


def clean(text):
    try:
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')
    except:
        pass
    text = text.replace('\n', ' ')
    return text


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
            try:
                setattr(self, key, clean(val))
            except:
                setattr(self, key, val)
        self._ientify_country()
        self._identify_sections()

    def _ientify_country(self):
        ''' return the country '''
        try:
            country = [f.name.lower() for f in pycountry.countries]
            ad = self.address.lower()
            self.country = country[
                map(lambda x: x in str(ad), country).index(True)]
        except:
            if 'taiwan' in ad:
                self.country = 'taiwan, province of china'
            elif 'south korea' in ad:
                self.country = "korea, democratic people's republic of"
            elif 'russia' in ad:
                self.country = 'russian federation'
            elif 'kyrgyz' in ad:
                self.country = 'kyrgyzstan'
            elif 'iran' in ad:
                self.country = 'iran, islamic republic of'
            elif 'tanzania' in ad:
                self.country = 'tanzania, united republic of'
            elif 'vietnam' in ad:
                self.country = 'viet nam'
            elif 'ivoire' in ad:
                self.country = "cote d'ivoire"
            elif 'bolivia' in ad:
                self.country = 'bolivia, plurinational state of'
            elif 'syria' in ad:
                self.country = 'syrian arab republic'
            elif 'north korea' in ad:
                self.country = 'korea, republic of'
            elif 'macedonia' in ad:
                self.country = 'macedonia, republic of'
            elif 'venezuela' in ad:
                self.country = 'venezuela, bolivarian republic of'
            elif 'usa' in ad:
                self.country = 'united states'
            elif 'lao' in ad:
                self.country = "lao people's democratic republic"
            elif 'reunion' in ad:
                self.country = 'reunion'
            elif 'brunei' in ad:
                self.country = 'brunei darussalam'
            elif 'virgin islands' in ad:
                self.country = 'virgin islands, british'
            elif 'micronesia' in ad:
                self.country = 'micronesia, federated states of'
            elif 'palestinian' in ad:
                self.country = 'palestine, state of'
            elif 'maryland eastern shore' in ad:
                self.country = 'united states'
            else:
                self.country = ad

    def _tag_to_tagsections(self, tag):
        tag_section = tag[:2]
        if tag[1] in [str(i) for i in range(10)]:
            tag_section = tag[0]
        return tag_section

    def _identify_sections(self):
        tags = [str(f).split(':')[0] for f in self.papers]
        self.tag_sections = [self._tag_to_tagsections(tag) for tag in tags]


def get_all_contrib(year):
    ''' Go looking for all the files and load it as a list of
    Paper object '''

    names = os.listdir(os.path.join(racine, 'Data', year))
    names = [f for f in names if f.split(
        '_')[-1] == 'V1.json' and f.split('_')[0] == 'Name']
    contributors = []
    for json in tqdm(names):
        json_file = os.path.join(racine, 'Data', year, json)
        try:
            contributors += [Contributor(key, val) for key, val
                             in load_json(json_file)['names'].iteritems()]
        except:
            pass

    # Missed one
    missed_contribs = [f for f in contributors if f.name.split(' ')[0] ==
                       'Test' or f.address == u'']

    [contributors.remove(miss) for miss in missed_contribs]

    return contributors
