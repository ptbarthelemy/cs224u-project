import sys, os, nltk, itertools, string, random
from re import findall
from extract_poem_features import getPoemModel
from sklearn.feature_extraction import DictVectorizer
from sklearn import datasets, linear_model
from numpy import mean
from random import shuffle
import pickle
from os.path import isfile

from extract_comment_features import getAffectRatios

# USE_FEATURE_LIST = ['typeTokenRatio', 'slantRhymeScore']
USE_FEATURE_LIST = ['posWords', 'conWords', 'typeTokenRatio']
META_DIRECTORY = "../data/meta"


def getScore(text):
    result = findall(r"rating:\s+(\d+.\d)", text)
    if len(result) > 0:
        return float(result[0])
    return None

def getPoemScores():
    scores = {}
    for filename in os.listdir(META_DIRECTORY):
        with open(META_DIRECTORY+'/'+filename) as f:
            scores[filename] = getScore(f.read())
    return scores

def filterFeatures(featureDict):
    # could change this to return all
    return dict((key, val) for key,val in featureDict.items()
        if key in USE_FEATURE_LIST)

def tenFold(features, scores, featureNames):
    rssTest = []
    rssTrain = []
    rssTestBenchmark = []
    rssTrainBenchmark = []
    for iteration in xrange(10):
        # partition data
        start = iteration*(len(features) / 10)
        end = start + (len(features) / 10)
        trainFeatures = features[0:start+1]
        trainFeatures.extend(features[end:])
        trainScores = scores[0:start+1]
        trainScores.extend(scores[end:])
        testFeatures = features[start:end]
        testScores = scores[start:end]

        # train
        regr = linear_model.LinearRegression()
        regr.fit(trainFeatures, trainScores)
        rss = mean((regr.predict(trainFeatures) - trainScores) ** 2)
        rssTrain.append(rss)

        # test
        rss = mean((regr.predict(testFeatures) - testScores) ** 2)
        rssTest.append(rss)

        # benchmark
        meanScore = mean(trainScores)
        rss = mean((meanScore - trainScores) ** 2)
        rssTrainBenchmark.append(rss)
        rss = mean((meanScore - testScores) ** 2)
        rssTestBenchmark.append(rss)

        # print weight info
        print "  iteration", iteration
        print "  coefficients"
        for key, val in zip(featureNames, regr.coef_):
            print "    ", key, ",",  val
        print "  residual sum of squares: %.2f" % rss

    trainError = mean(rssTrain)
    testError = mean(rssTest)
    benchmarkTrainError = mean(rssTrainBenchmark)
    benchmarkTestError = mean(rssTestBenchmark)

    print "------------------------------------------------"
    print "Mean RSS value |    base |  result | improves by"
    print "------------------------------------------------"
    print "  train error  |    %0.2f |    %0.2f |      %0.2f%%" % \
        (benchmarkTrainError, trainError, 
        ((benchmarkTrainError - trainError) * 100/ benchmarkTrainError))
    print "  test error   |    %0.2f |    %0.2f |      %0.2f%%" % \
        (benchmarkTestError, testError, 
        ((benchmarkTestError - testError) * 100/ benchmarkTestError))
    print "------------------------------------------------"

        
if __name__ == "__main__":
    dataFileName = "data.list"

    print "Extracting features..."
    poems = getPoemModel().poems

    # try to predict poem score or affect ratio
    # scores = getPoemScores()
    scores = getAffectRatios()

    print "Finding metadata info..."
    filenames = poems.keys()[:]
    shuffle(filenames) # don't want all of the good ones to show up first
    featureArr = []
    scoreArr = []
    for filename in filenames:
        score = scores.get(filename, None)
        if score is None:
            # skip poems without ratings
            print "  no rating for", filename
            continue 

        featureSet = poems.get(filename, None)
        if featureSet is None:
            # only include poem if features are extracted for it
            print "  no features for", filename
            continue

        scoreArr.append(score)
        featureArr.append(filterFeatures(featureSet))

        # # print featureArr for specific poem
        # print "poem", f
        # for key, value in poems[f].items():
        #     print "  ", key, ":", value

    vec = DictVectorizer()
    featureArr = vec.fit_transform(featureArr).toarray().tolist()
    featureNames = vec.get_feature_names()

    print "Performing regression using %d data points..." % len(scoreArr)
    tenFold(featureArr, scoreArr, featureNames)
