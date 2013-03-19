import sys
from scipy.stats.stats import pearsonr
import matplotlib.pyplot as plt
import numpy as np


def plotFeatureVsScore(poems, scores, feature):
    x, y = [], []
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
    label = "p < 0.0001" if pearP < 0.0001 else "p = %0.4f"%pearP
    plt.plot(np.array(x), np.array(x) * m + c,color="red", label=label)
    plt.legend(loc=3)

    print feature, " correlation: %0.3f pvalue: %0.3f" % (correl, pearP)

def makePlots(xDict, yDict, yname="score", filename="feature_scatter.jpg"):
    # xDict is a dict of dicts, the latter or which map feature to value
    print "Plotting %d feature plots..." % len(next(iter(xDict.values())))
    plt.figure(num=None, figsize=(24, 18), dpi=80, facecolor='w',
        edgecolor='k')
    for index, feature in enumerate(next(iter(xDict.values())).keys()):
        plt.subplot(5, 6, 1 + index)
        plotFeatureVsScore(xDict, yDict, feature)

    plt.suptitle("features vs. %s" % yname, fontsize=20)
    plt.savefig(filename, format="jpg")

def blowUpPlots(xDict, yDict):
    useFeatures = ['posWords', 'conWords', 'typeTokenRatio']
    print "Plotting %d feature plots..." % len(useFeatures)
    for index, feature in enumerate(next(iter(xDict.values())).keys()):
        if feature not in useFeatures:
            continue
        plt.figure(num=None, figsize=(16, 12), dpi=80, facecolor='w', edgecolor='k')
        plotFeatureVsScore(xDict, yDict, feature)
        plt.savefig("zoom_%s.jpg" % feature, format="jpg")

def makeHistogram(affectHist, filename):
    plt.figure(num=None, figsize=(12, 6), dpi=80)
    cats = sorted(next(iter(affectHist.values())).keys())
    for hist in affectHist.values():
        plt.plot(range(len(cats)), 
            [hist.get(cat,0) for cat in cats],
            color="blue", alpha=0.2)

    plt.ylabel("prevalence")
    plt.xlabel("emotional category")
    plt.xticks(range(len(cats)), cats)
    plt.savefig(filename, format="jpg")


if __name__ == "__main__":
    pass
