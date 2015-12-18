import json,codecs

def load_json(name):
    with codecs.open(name, 'r','utf8') as f:
        return json.load(f)    
        
class Paper(object):
    ''' handle each paper submitted to AGU data base '''

    def __init__(self,link,data):
        self.link = link
        for key,val in data.iteritems():
            setattr(self,key,val)


