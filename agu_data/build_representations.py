import os
import re
import time
import sys
import sklearn
import pickle
from sklearn import manifold
from sklearn.externals import joblib
from tqdm import *
from os.path import expanduser
import numpy as np
home = expanduser('~')
os.chdir(os.path.join(home, 'Documents', 'project',
                      'agu_data', 'repo', 'agu_data'))
from Data_Utils import *
import nltk
from nltk.stem.snowball import SnowballStemmer
import gensim
from gensim import corpora, models, similarities
from pprint import pprint
model_saved = os.path.join(
    home, 'Documents', 'project', 'agu_data', 'repo', 'Notebook', 'Models')

################################################
# Get the args
name = sys.argv[1]
add_bigram = sys.argv[2]
if add_bigram == 'True':
    add_bigram = True
elif add_bigram == 'False':
    add_bigram = False
else:
    raise ValueError('Second arg must be either True of False (bigrams)')

if not os.path.isdir(os.path.join(model_saved, 'gensim', name)):
    os.mkdir(os.path.join(model_saved, 'gensim', name))
abstractf = os.path.join(model_saved, 'gensim', name, name)
print abstractf

##################################################
# Get the data
data = get_all_data('agu2015')
sources = [df for df in data if (''.join(df.title) != "") and (
    df.abstract != '') and (len(df.abstract.split(' ')) > 100)]
abstracts = get_clean_abstracts(sources)
titles = get_clean_titles(sources)

# abstracts = abstracts[:100]
# titles = titles[:100]

##################################################
# Build Bow_To_Vec_Representation

build = False
if build:
    print 'Building the bow representation'
    # First, write the document corpus on a txt file, one document perline.
    write_clean_corpus(abstracts, abstractf + '_data.txt')

    # Initialize the model
    bow_corpus = MyCorpus(abstractf, add_bigram=add_bigram)
    # load the dictionary
    # Next create the dictionary by iterating of the abstract, one per line in
    # the txt file
    dictionary = corpora.Dictionary(bow_corpus.tokenize_and_stem(
        line) for line in open(abstractf + '_data.txt'))
    dictionary.save(abstractf + '_raw.dict')
    dictionary.filter_extremes(no_below=5, no_above=0.80, keep_n=200000)
    dictionary.id2token = {k: v for v, k in dictionary.token2id.iteritems()}
    dictionary.save(abstractf + '.dict')
    # Builde corpus
    bow_corpus.load_dict()
    corpora.MmCorpus.serialize(abstractf + '_bow.mm', bow_corpus)
    # index for similarities
    index_bow = similarities.SparseMatrixSimilarity(bow_corpus,
                                                    num_features=len(dictionary))
    index_bow.save(abstractf + '_bow.index')

##################################################
# Build Tf-idf representation

build = False
if build:
    print 'Building the tfidf representation'
    # First load the corpus and the dicitonary
    bow_corpus = corpora.MmCorpus(abstractf + '_bow.mm')
    dictionary = corpora.Dictionary.load(abstractf + '.dict')
    # Initialize the tf-idf model
    tfidf = models.TfidfModel(bow_corpus)
    # Compute the tfidf of the corpus itself
    tfidf_corpus = tfidf[bow_corpus]
    # Serialize both for reuse
    tfidf.save(abstractf + '_tfidf.model')
    corpora.MmCorpus.serialize(abstractf + '_tfidf.mm', tfidf_corpus)
    # index for similarities
    index_tfidf = similarities.SparseMatrixSimilarity(tfidf_corpus,
                                                      num_features=len(dictionary))
    index_tfidf.save(abstractf + '_tfidf.index')

##################################################
# Build lsa representation
build = False
num_topics = 500
if build:
    print 'Building the lsi representation'
    # First load the corpus and the dicitonary
    tfidf_corpus = corpora.MmCorpus(abstractf + '_tfidf.mm')
    dictionary = corpora.Dictionary.load(abstractf + '.dict')
    # Initialize the LSI model
    lsi = models.LsiModel(tfidf_corpus, id2word=dictionary,
                          num_topics=num_topics)
    # Compute the tfidf of the corpus itself
    lsi_corpus = lsi[tfidf_corpus]
    # Serialize both for reuse
    lsi.save(abstractf + '_lsi.model')
    corpora.MmCorpus.serialize(abstractf + '_lsi.mm', lsi_corpus)

    # index for similarities
    index_tfidf = similarities.MatrixSimilarity(lsi_corpus,
                                                num_features=num_topics)
    index_tfidf.save(abstractf + '_lsi.index')

##################################################
# Build the t-sne represenation
build = True
if build:
    tsne = manifold.TSNE(n_components=2, init='pca',
                         random_state=0, metric='cosine')
    lsi_corpus = corpora.MmCorpus(abstractf + '_lsi.mm')
    X = gensim.matutils.corpus2dense(
        lsi_corpus, num_terms=lsi_corpus.num_terms)
    X_data = np.asarray(X).astype('float64')
    X_tsne = tsne.fit_transform(X_data.T)
    joblib.dump(X, abstractf + '_X.pkl')
    joblib.dump(X_tsne, abstractf + '_Xtsne.pkl')
