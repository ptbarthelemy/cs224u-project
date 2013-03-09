# classifies poems against labels from comments, runs 10-fold cross-validation with a maxent classifier
# usage: python classify.py [poem_dir] [comments_dir]
# 'NRC-lexicon.txt' must be in the right directory (currently '../data/')

import sys, os, nltk, itertools, string, random
from kl import kldiv
import numpy as np
from nltk.classify import maxent
from collections import defaultdict
from operator import itemgetter
from extract_poem_features import PoemModel

# for saving/opening file
import pickle
from os.path import isfile


# prior code for iterating through classifiers
'''
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
'''


# maps categories to indices (i.e. dimensions) so we can use real-valued features
cats = ['anger', 'anticipation', 'disgust', 'fear', 'joy', 'sadness', 'surprise', 'trust']

lex = open('../data/NRC-lexicon.txt')
lex_dict = {}
for l in lex:
    if l.split()[0] not in lex_dict:
        lex_dict[l.split()[0]]=set([])
    if l.split()[2] == '1':
        lex_dict[l.split()[0]].add(l.split()[1])


def get_label(comments):
    # this function gets the label(s) from a comments file
    # current implementation represents this as a list where emotional values are scaled to 100
    # and for a given featureset (poem) the classifier is trained on 100 examples using this
    # distribution of labels

    # note: these values are normalized to sum to 1, not to 100

    counts = [0]*8
    for cl in comments:
        #neg = False
        for w in cl.split('|||')[1].split():
            s = ''.join(ch for ch in w.lower() if ch not in string.punctuation)
            if s in lex_dict:
                for key in lex_dict[s]:
                    if key != 'positive' and key != 'negative':
                        counts[cats.index(key)]+=1

    if all(x == 0 for x in counts):
        return 'empty'
    
    # scale to 100 and make sure there are exactly 100 examples
    # if deficient randomly remove/add something that already exists in the counts
    label = [float(i)/sum(counts) for i in counts]

    return label
                
def doc_features(poem):
    featureset = defaultdict(int)
    total_words = 0.0
    for pl in poem:
        for w in pl.split():
            s = ''.join(ch for ch in w.lower() if ch not in string.punctuation)
            if s in lex_dict:
                for key in lex_dict[s]:
                    if key != 'positive' and key != 'negative':
                        featureset[key] += 1
                        total_words += 1.0
    return featureset

def ten_fold(data):
    results = []
    for iteration in [0]: #xrange(10):
        train_set, test_set, train_labels, test_distributions=[],[],[],[]
        start = iteration*(len(data)/10)
        end = start + (len(data)/10)

        # scale label to 100

        joint_features = []
        for i, item in enumerate(data):
            if i >= start and i < end:
                test_set.append(item[0])
                test_distributions.append(item[1])
            else:
                # normalize label to 100 w ints for training examples
                label = [int(x*100) for x in item[1]]

                while sum(label) != 100:
                    rand = random.randint(0, len(cats) - 1)
                    if sum(label) < 100:
                        if item[1][rand] > 0.0:
                            label[rand] += 1
                    elif sum(label) > 100:
                        if label[rand] > 0:
                            label[rand] -= 1

                for j, count in enumerate(label):
                    for k in xrange(count):
                        train_set.append(item[0])
                        train_labels.append(cats[j])
                        joint_features.append((item[0],cats[j]))

        print >> sys.stderr, iteration, 'th iteration'
        print >> sys.stderr, len(train_set), 'training examples'

        # training        
        features = maxent.TypedMaxentFeatureEncoding.train(joint_features)
        print 'features encoded'
        classifier = nltk.MaxentClassifier.train(joint_features,algorithm='IIS',max_iter=2)
        
        # testing
        kl_stats = []
        for f, l in itertools.izip(test_set,test_distributions):
            classout = [0.]*8
            probdist = classifier.prob_classify(f)
            for item in probdist.samples():
                classout[cats.index(item)] = probdist.prob(item)
            '''
            print classout
            print l
            print kldiv(l,classout)
            print ''
            '''
            kl_stats.append(kldiv(l,classout))
            
        results.append(float(sum(kl_stats))/len(kl_stats))
        print results
        

def main():
    # execute with parameters <poem-directory> <comment-directory>
    dataFileName = "data.list"
    if not isfile("data.list"):
        print "Processing data..."
        data = []
        poems = PoemModel(sys.argv[1]).poems
        for i, f in enumerate(sorted(os.listdir(sys.argv[2]))):
            comment_f = open(sys.argv[2]+'/'+f).readlines()
            poem = poems[f]

            # this line removes poems from consideration if they have fewer than 10 comments - comment this out if you want to consider all poems
            if len(comment_f) < 10: continue

            label = get_label(comment_f)
            #print label
            if label == 'empty': continue
            data.append((poem, label))
            pickle.dump(data, open(dataFileName, "wb"))
    else:
        print "Loading data file..."
        data = pickle.load(open(dataFileName, "rb"))

    # calculate some stats
    klvalues = []
    for i, (_, l1) in enumerate(data):
        for j, (_, l2) in enumerate(data):
            klvalues.append(kldiv(l1, l2))
    print "average klvalue of any pair of distributions", np.mean(klvalues)
    distAverage = [sum(a) for a in zip(*[b for a,b in data])] # this isn't normalized, but it doesn't matter
    klvalues = []
    for i, (_, l1) in enumerate(data):
        klvalues.append(kldiv(l1, distAverage))
    print "average klvalue relative to average distribution", np.mean(klvalues)

    ten_fold(data)

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
