import sys
from scipy.stats.stats import pearsonr
import matplotlib.pyplot as plt
import numpy as np

from extract_poem_features import getPoemModel
from poem_predict_rating import getPoemScores
from extract_comment_features import getAffectRatios, getAffectHistograms


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
    label = "p < 0.0001" if pearP < 0.0001 else "p = %0.4f"%pearP
    plt.plot(np.array(x), np.array(x) * m + c,color="red", label=label)
    plt.legend(loc=3)

    print feature, " correlation: %0.3f pvalue: %0.3f" % (correl, pearP)

def makePlots(xDict, yDict):
    # xDict is a dict of dicts, the latter or which map feature to value
    print "Plotting %d feature plots..." % len(next(iter(xDict.values())))
    plt.figure(num=None, figsize=(24, 18), dpi=80, facecolor='w', edgecolor='k')
    for index, feature in enumerate(next(iter(xDict.values())).keys()):
        plt.subplot(3, 4, 1 + index)
        plotFeatureVsScore(xDict, yDict, feature)
    plt.savefig("feature_scatter.jpg", format="jpg")

def blowUpPlots(xDict, yDict):
    useFeatures = ['posWords', 'conWords', 'typeTokenRatio']
    print "Plotting %d feature plots..." % len(useFeatures)
    for index, feature in enumerate(next(iter(xDict.values())).keys()):
        if feature not in useFeatures:
            continue
        plt.figure(num=None, figsize=(16, 12), dpi=80, facecolor='w', edgecolor='k')
        plotFeatureVsScore(xDict, yDict, feature)
        plt.savefig("zoom_%s.jpg" % feature, format="jpg")

def makeHistogram():
    plt.figure(num=None, figsize=(16, 12), dpi=80)
    affectHist = getAffectHistograms()
    cats = sorted(next(iter(affectHist.values())).keys())
    for hist in affectHist.values():
        plt.plot(range(len(cats)), 
            [hist.get(cat,0) for cat in cats],
            color="blue", alpha=0.2)

    plt.ylabel("prevalence")
    plt.xlabel("emotional category")
    plt.xticks(range(len(cats)), cats)
    plt.savefig("emotional_histograms.jpg", format="jpg")


if __name__ == "__main__":
    # scatter plots
    print "Extracting features..."
    m = getPoemModel()
    poems = m.poems
    print "Finding y-values..."
    # scores = getPoemScores() # plot voter scores
    scores = getAffectRatios()  # plot affect ratios
    makePlots(poems, scores)
    blowUpPlots(poems, scores)

    # # make histogram
    # makeHistogram()