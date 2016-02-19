######## IMPORT    #########
import json
import codecs
import os
import re
import time
from tqdm import *
from os.path import expanduser
import pandas as pd
import unicodedata
import pycountry
from gensim import corpora, models, similarities
import nltk
from nltk.stem.snowball import SnowballStemmer

######## PARAMETER #########
home = expanduser("~")
racine = os.path.join(home, 'Documents', 'project',
                      'agu_data', 'repo', 'agu_data')
year = 'agu2014'

###### FUNCTIONS #########


class MyCorpus(object):

    def __init__(self, name):
        self.name = name
        self.stopwords = nltk.corpus.stopwords.words('english')
        self.stemmer = nltk.stem.snowball.SnowballStemmer("english")
        self.load_dict()

    def load_dict(self):
        if not os.path.isfile(self.name + '.dict'):
            print 'You should build the dictionary first !'
        else:
            setattr(self, 'dictionary',
                    corpora.Dictionary.load(self.name + '.dict'))

    def tokenize_and_stem(self, text):
        tokens = [word.lower() for sent in nltk.sent_tokenize(text)
                  for word in nltk.word_tokenize(sent)]
        filtered_tokens = []
        bad_tokens = []
        # filter out any tokens not containing letters (e.g., numeric tokens, raw
        # punctuation)
        for token in tokens:
            if re.search('(^[a-z]+$|^[a-z][\d]$|^[a-z]\d[a-z]$|^[a-z]{3}[a-z]*-[a-z]*$)', token):
                filtered_tokens.append(token)
            else:
                bad_tokens.append(token)
        filtered_tokens = [
            token for token in filtered_tokens if token not in self.stopwords]
        stems = map(self.stemmer.stem, filtered_tokens)
        return map(str, stems)

    def __iter__(self):
        for line in open(self.name + '.txt'):
            # assume there's one document per line, tokens separated by
            # whitespace
            yield self.dictionary.doc2bow(self.tokenize_and_stem(line))


def load_json(name):
    with codecs.open(name, 'r', 'utf8') as f:
        return json.load(f)


def write_clean_corpus(corpus, path):
    with open(path, 'w+') as f:
        for elt in corpus:
            f.write(elt + '\n')


def clean_abstract(text):
    ''' Clean an abstract '''
    if text.split('\n')[0].split(' ')[0] == 'ePoster':
        text = ' '.join(text.split('\n')[1:])
    try:
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')
    except:
        pass
    text = text.replace('\n', ' ')
    return text


def get_raw_titles(sources):
    raw_titles = [' '.join(df.title) for df in sources]
    return raw_titles


def clean_title(text):
    if text.split(' ')[-1] == '(Invited)':
        text = ' '.join(text.split(' ')[:-1])
    try:
        text = unicodedata.normalize('NFKD', text).encode('ascii', 'ignore')
    except:
        pass
    text = text.replace('\n', ' ')
    return text


def get_raw_abstracts(sources):
    raw_abstracts = [df.abstract for df in sources]
    return raw_abstracts


def get_clean_titles(sources):
    ''' Return a clean version of the  abstract corpus '''

    raw_titles = get_raw_titles(sources)
    titles = map(clean_title, raw_titles)
    return titles


def get_clean_abstracts(sources):
    ''' Return a clean version of the  abstract corpus '''

    raw_abstracts = get_raw_abstracts(sources)
    abstracts = map(clean_abstract, raw_abstracts)
    return abstracts

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
