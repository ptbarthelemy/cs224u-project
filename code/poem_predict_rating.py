import sys, os, nltk, itertools, string, random, numpy
from re import findall
from extract_poem_features import PoemModel
from sklearn.feature_extraction import DictVectorizer
from sklearn import datasets, linear_model
from random import shuffle

# for saving/opening file
import pickle
from os.path import isfile

def getScore(text):
    result = findall(r"rating:\s+(\d+.\d)", text)
    if len(result) > 0:
        return float(result[0])
    return None

def tenFold(features, scores, featureNames):
    rssValues = []
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

        # test
        rss = numpy.mean((regr.predict(testFeatures) - testScores) ** 2)
        rssValues.append(rss)

        # # print output
        # print "  iteration", iteration
        # print "  coefficients"
        # for key, val in zip(featureNames, regr.coef_):
        #     print "    ", key, ",",  val
        # print "  residual sum of squares: %.2f" % rss

    print "  mean rss from all runs: %0.2f" % numpy.mean(rssValues)
        
if __name__ == "__main__":
    dataFileName = "data.list"
    poemDirectory = sys.argv[1]
    metaDirectory = sys.argv[2]

    print "Processing data..."
    features = []
    scores = []
    poems = PoemModel(poemDirectory).poems
    filenames = os.listdir(metaDirectory)
    shuffle(filenames) # don't want all of the good ones to show up first
    for i, f in enumerate(filenames):
        meta = open(metaDirectory+'/'+f).read()
        score = getScore(meta)
        if score is None:
            print "  skipping poem", f
            continue # skip poems without ratings
        scores.append(score)
        features.append(poems[f])
    vec = DictVectorizer()
    features = vec.fit_transform(features).toarray().tolist()
    featureNames = vec.get_feature_names()

    print "Benchmarking..."
    meanScore = numpy.mean(scores)
    print "  mean score", meanScore
    print "  residual sum of squares using average score: %.2f" % \
        numpy.mean((meanScore - scores) ** 2)

    print "Performing regression using %d data points..." % len(scores)
    tenFold(features, scores, featureNames)
