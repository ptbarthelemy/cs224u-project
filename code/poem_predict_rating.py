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

# # maps categories to indices (i.e. dimensions) so we can use real-valued features
# cats = ['anger', 'anticipation', 'disgust', 'fear', 'joy', 'sadness', 'surprise', 'trust']

# lex = open('../data/NRC-lexicon.txt')
# lex_dict = {}
# for l in lex:
#     if l.split()[0] not in lex_dict:
#         lex_dict[l.split()[0]]=set([])
#     if l.split()[2] == '1':
#         lex_dict[l.split()[0]].add(l.split()[1])


def get_label(metafile):
    # this function gets the label(s) from a comments file
    # current implementation represents this as a list where emotional values are scaled to 100
    # and for a given featureset (poem) the classifier is trained on 100 examples using this
    # distribution of labels

    # note: these values are normalized to sum to 1, not to 100
    print metafile.findall("rating:\w+(\d.\d)")
    return 0
                
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
        train_set, test_set, train_labels, test_labels=[],[],[],[]
        start = iteration*(len(data)/10)
        end = start + (len(data)/10)

        # scale label to 100

        joint_features = []
        for i, item in enumerate(data):
            if i >= start and i < end:
                test_set.append(item[0])
                test_labels.append(item[1])
            else:
                train_set.append(item[0])
                train_labels.append(item[1])
                joint_features.append((item[0],item[1]))

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
    dataFileName = "data.list"
    poemDirectory = sys.argv[1]
    metaDirectory = sys.argv[2]

    print "Processing data..."
    data = []
    poems = PoemModel(poemDirectory).poems
    for i, f in enumerate(sorted(os.listdir(metaDirectory))):
        meta = open(metaDirectory+'/'+f).readlines()
        poem = poems[f]
        label = get_label(meta)
        data.append((poem, label))

    # # calculate some stats
    # klvalues = []
    # for i, (_, l1) in enumerate(data):
    #     for j, (_, l2) in enumerate(data):
    #         klvalues.append(kldiv(l1, l2))
    # print "average klvalue of any pair of distributions", np.mean(klvalues)
    # distAverage = [sum(a) for a in zip(*[b for a,b in data])] # this isn't normalized, but it doesn't matter
    # klvalues = []
    # for i, (_, l1) in enumerate(data):
    #     klvalues.append(kldiv(l1, distAverage))
    # print "average klvalue relative to average distribution", np.mean(klvalues)

    ten_fold(data)

main()
