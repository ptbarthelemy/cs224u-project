import sys
from scipy.stats.stats import pearsonr
import matplotlib.pyplot as plt
import numpy as np

from extract_poem_features import getPoemModel
from poem_predict_rating import getPoemScores
from extract_comment_features import getAffectRatios

# def assignIDs(list):
#     '''Take a list of strings, and for each unique value assign a number.
#     Returns a map for "unique-val"->id.
#     '''
#     sortedList = sorted(list)

#     #taken from
#     #http://stackoverflow.com/questions/480214/how-do-you-remove-duplicates-from-a-list-in-python-whilst-preserving-order/480227#480227
#     seen = set()
#     seen_add = seen.add
#     uniqueList =  [ x for x in sortedList if x not in seen and not seen_add(x)]

#     return  dict(zip(uniqueList,range(len(uniqueList))))

def plotFeatureVsScore(poems, scores, feature):
    x = []
    y = []
    for key, value in poems.items():
        if scores.get(key, None) is None:
            continue
        x.append(value.get(feature))
        y.append(scores.get(key))
    correl, pearP = pearsonr(x, y)

    # least squares from:http://docs.scipy.org/doc/numpy/reference/generated/numpy.linalg.lstsq.html
    A = np.vstack([x, np.ones(len(x))]).T
    m, c = np.linalg.lstsq(A, np.array(y))[0]

    plt.scatter(x, y)
    plt.xlabel(feature)
    plt.plot(np.array(x), np.array(x) * m + c,color="red", label="p = %0.4f"%pearP)
    plt.legend(loc=3)
    print feature, " correlation: %0.3f pvalue: %0.3f" % (correl, pearP)

def makePlots(xDict, yDict):
    # xDict is a dict of dicts, the latter or which map feature to value
    print "Plotting %d feature plots..." % len(next(iter(xDict.values())))
    plt.figure(num=None, figsize=(24, 18), dpi=80, facecolor='w', edgecolor='k')
    for index, feature in enumerate(next(iter(xDict.values())).keys()):
        plt.subplot(3, 4, 1 + index)
        plotFeatureVsScore(xDict, yDict, feature)
    plt.savefig("feature_scatter.pdf", format="pdf")

if __name__ == "__main__":
    print "Extracting features..."
    m = getPoemModel()
    poems = m.poems

    print "Finding y-values..."
    # scores = getPoemScores() # plot voter scores
    scores = getAffectRatios()  # plot affect ratios

    makePlots(poems, scores)