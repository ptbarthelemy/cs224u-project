# classifies poems against labels from comments, runs 10-fold cross-validation with a maxent classifier
# usage: python classify.py [poem_dir] [comments_dir]
# 'NRC-lexicon.txt' must be in the working directory

import sys, os, nltk, itertools, string
import numpy as np
from collections import defaultdict
from operator import itemgetter
from sklearn.naive_bayes import MultinomialNB
from sklearn.naive_bayes import BernoulliNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.linear_model import LogisticRegression

classifiers = [
    KNeighborsClassifier(3),
    SVC(kernel="linear", C=0.025),
    SVC(gamma=2, C=1),
    DecisionTreeClassifier(max_depth=5),
    RandomForestClassifier(max_depth=5, n_estimators=10, max_features=1),
    GaussianNB(),
    MultinomialNB(),
    BernoulliNB(),
    LogisticRegression()]

# maps categories to indices (i.e. dimensions) so we can use real-valued features
cats = ['anger', 'anticipation', 'disgust', 'fear', 'joy', 'sadness', 'surprise', 'trust']

# these were dicts for a kinda weird negation thing i was trying out
'''
opposites = {'anger' : 'trust','trust': 'anger', 'anticipation': 'fear', 'fear': 'anticipation', 'joy': 'sadness', 'sadness': 'joy', 'surprise': 'disgust', 'disgust': 'surprise'}
negs = set(['no','not','never','wont','cant'])
'''


lex = open('NRC-lexicon.txt')
lex_dict = {}
for l in lex:
    if l.split()[0] not in lex_dict:
        lex_dict[l.split()[0]]=set([])
    if l.split()[2] == '1':
        lex_dict[l.split()[0]].add(l.split()[1])

def get_label(comments):
    # this function gets the label from a comments file, current implementation just adds up the 
    mc_c = defaultdict(int)
    for cl in comments:
        #neg = False
        for w in cl.split('|||')[1].split():
            s = ''.join(ch for ch in w.lower() if ch not in string.punctuation)
            if s in lex_dict:
                for key in lex_dict[s]:
                    if key != 'positive' and key != 'negative':
                        #if neg:
                            #mc_c[opposites[key]] += 1
                            #print 'negged: ', w
                        #else:
                        mc_c[key] += 1
            #elif s in negs:
                #neg = True
            #for ch in string.punctuation:
                #if ch in w.lower():
                    #neg = False
    if len(mc_c) > 0: label = cats.index(max(mc_c.iteritems(), key = itemgetter(1))[0])
    else: label = -1
    return label

def doc_features(poem):
    featureset = []
    emo_words = defaultdict(int)
    total_words = 0.0
    for pl in poem:
        for w in pl.split():
            s = ''.join(ch for ch in w.lower() if ch not in string.punctuation)
            if s in lex_dict:
                for key in lex_dict[s]:
                    if key != 'positive' and key != 'negative':
                        emo_words[key] += 1
                        total_words += 1.0
    for key in cats:
        if key in emo_words:
            featureset.append(emo_words[key]/total_words)
        else:
            featureset.append(0.0)
    #print featureset
    return featureset

def evaluate(classifier, test):
    c = 0
    w = 0
    for sample in test:
        #print sample[1], classifier.classify(sample[0])
        if sample[1] == classifier.classify(sample[0]):
            c += 1
        else:
            w += 1
    return c/(c+w)

def ten_fold(data, classifier):
    results = []
    cd = defaultdict(int)
    wd = defaultdict(int)

    for i in xrange(10):
        train_set, test_set, train_labels, test_labels=[],[],[],[]
        start = i*(len(data)/10)
        end = start + (len(data)/10)
        for i, item in enumerate(data):
            if i >= start and i < end:
                test_set.append(item[0])
                test_labels.append(item[1])
            else:
                train_set.append(item[0])
                train_labels.append(item[1])

        train = np.array(train_set)
        labels = np.array(train_labels)
        classifier.fit(train,labels)

        c = 0.
        w = 0.
        for s, l in itertools.izip(test_set,test_labels):
            #print classifier.predict(s)
            #print l
            if classifier.predict(s) == l:
                c+=1
                cd[cats[l]]+=1
            else:
                w+=1
                wd['was '+cats[l]+' but we guessed '+cats[int(classifier.predict(s)[0])]]+=1
        results.append(c/(c+w))
        '''
        if str(classifier).startswith('Logistic'):
            print classifier.decision_function(test_set[0])
        '''

    print '\n*****************'
    print '\nCURRENT CLASSIFIER:', str(classifier)
    print '10-fold cross-validation average accuracy: ',sum(results)/len(results) # print 10-fold average
    print '\nmost common correct ones'
    for item in sorted(cd.iteritems(), key = itemgetter(1), reverse = True):
        print item 

    print '\nmost common wrong ones'
    for item in sorted(wd.iteritems(), key = itemgetter(1), reverse = True):
        print item

def main():
    data = []
    for i in sorted(os.listdir(sys.argv[1])):
        poem_f = open(sys.argv[1]+'/'+i).readlines()
        comment_f = open(sys.argv[2]+'/'+i).readlines()
        if len(comment_f) < 10: continue   # this line removes poems from consideration if they have less than 10 comments - comment this out if you want to consider all poems
        data.append((doc_features(poem_f), get_label(comment_f)))
    print len(data)
    for classifier in classifiers:
        ten_fold(data, classifier)

main()
















#old code for maxent with nltk
'''
    results = []
    for i in xrange(10):
        train_set, test_set = [], []
        start = i*(len(data)/10)
        end = start + (len(data)/10)
        print start, end
        for i, item in enumerate(data):
            if i >= start and i < end:
                test_set.append(item)
            else:
                train_set.append(item)
        print len(train_set), len(test_set)
        classifier = nltk.MaxentClassifier.train(train_set, max_iter=10)
        results.append(evaluate(classifier, test_set))

    print results
'''    
