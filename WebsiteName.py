__author__ = 'baslersean'

"""
We are trying to come up with a name for a new startup. The name has to satisfy two hard requirements:
The .com domain should be available, and there should not be another company that has trademarked the name.
The other part that is complicated is the need to come up with names to test.
"""

# function that takes as input the name and checks if the .com domain that corresponds to that name is available.
def domaincheck(name):
    import json
    import requests

    url = "http://freedomainapi.com/?key=vn4nblu1w7&domain=%s.com" % name
    response = requests.get(url)
    response.text

    data = json.loads(response.text)
    return data["available"]

# function that checks if the trademark is available for registration by crawling
def trademarkcheck(name):
    import requests # This command allows us to fetch URLs
    from lxml import html # This module will allow us to parse the returned HTML/XML
    import pandas # To create a dataframe

    # Let's start by fetching the page, and parsing it
    url = 'http://www.trademarkia.com/trademarks-search.aspx?tn=%s' % (name)
    response = requests.get(url) # get the html of that url
    doc = html.fromstring(response.text) # parse it and create a document

    text = [lnk.text_content() for lnk in doc.findall('.//*[@id="right"]')]

    search = "This name is not found in our database of U.S. trademarks"

    if any([search in s for s in text]):
        return True
    else:
        return False

# Use WordNet, and its feature: the hyponyms, to get as input a general term (e.g., mammal), find the appropriate sense
# across the different synonyms sets (Synsets), and the find all the hyponyms that are "under" the term (e.g., find all
# the mammals).
def idealist(category):
    from nltk.corpus import wordnet as wn

    word = wn.synsets(category)[0]
    hypo = lambda s: s.hyponyms()

    mylist = list(word.closure(hypo))

    newlist = [str(lemma.name()) for lemma in mylist]

    # clean up list by removing Synset structure and underscores (so it can be processed properly by the domain searcher
    finallist = [ x[:-5] for x in newlist ]
    finallist = [w.replace('_', '') for w in finallist]

    return finallist

# Test each of the terms in the list, and see if it qualifies as a viable company name (i.e., it has an available domain
# name and trademark).
term = raw_input("Enter proposed company name: ")
print "Proposed Company Name: ", term
print "Domain Available: ", domaincheck(term)
print "Trademark Available: ", trademarkcheck(term)
if domaincheck(term) == True and trademarkcheck(term) == True:
    print "QUALIFYING"
else:
    print"NON-QUALIFYING"


answerlist = idealist('dog')
data = []

for term in answerlist:
    print "Term: ", term
    print "Domain Available: ", domaincheck(term)
    print "Trademark Available: ", trademarkcheck(term)
    print "=========================="

    #save data in list
    if domaincheck(term) == True and trademarkcheck(term) == True:
        data += [("Y", term)]
    else:
        data += [("N", term)]

# Analyze the length of the qualifying and non-qualifying names, and create a conditional frequency distribution for the
# word lengths of the two categories (qualifying names and non-qualifying names). Plot the result by showing how many
# names have a specific length (in characters) and belong to the qualifying set, and how many belong to the
# "non-qualifying" set.

import nltk

wordlength = [(label, term[0]) for (label, term) in data]

cfd = nltk.ConditionalFreqDist(wordlength)

import pandas as pd
import matplotlib.pyplot as plt
# Make the graphs a bit prettier, and bigger
pd.set_option('display.mpl_style', 'default')
plt.rcParams['figure.figsize'] = (15, 5)

cfd.plot()

# Create a classifier that can separate qualifying from non-qualifying company names.
from nltk.corpus import names
import random

def word_features(word):

    return {
        'length': len(word),
    }

labeled_featuresets = [(word_features(name), response) for (response, name) in data]

train_set, test_set = [], []
trials = 50
psum = 0;
cnt = 0;
for i in range(trials):
    random.shuffle(labeled_featuresets)

    train_set, test_set = labeled_featuresets[100:], labeled_featuresets[:100]
    classifier = nltk.NaiveBayesClassifier.train(train_set)
    accuracy = nltk.classify.accuracy(classifier, test_set)
    print("Trial:", cnt, " Accuracy:", accuracy)
    psum += accuracy
    cnt += 1

print "Avg Accuracy: ", (psum/cnt)

# Test classifier
classifier.classify(word_features('TestName'))