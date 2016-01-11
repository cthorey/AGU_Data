######## IMPORT    #########
import json
import codecs
import os
import time
from tqdm import *

######## PARAMETER #########
root = '/Users/thorey/Documents/MLearning/Side_Project/AGU_Data/'


###### FUNCTIONS #########

def load_json(name):
    with codecs.open(name, 'r', 'utf8') as f:
        return json.load(f)


class Paper(object):
    ''' handle each paper submitted to AGU data base '''

    def __init__(self, link, data):
        self.link = link
        for key, val in data.iteritems():
            setattr(self, key, val)


def get_all_data(year):
    ''' Go looking for all the files and load it as a list of
    Paper object '''

    name = os.listdir(os.path.join(root, 'Data', year))
    name = [f for f in name if f.split('_')[-1] == 'V2.json']
    papers = []
    for json in tqdm(name):
        json_file = os.path.join(root, 'Data', year, json)
        papers += [Paper(key, val) for key, val
                   in load_json(json_file)['papers'].iteritems()]

    return papers
