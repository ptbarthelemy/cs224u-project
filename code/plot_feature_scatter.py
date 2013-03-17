import sys
from scipy.stats.stats import pearsonr
import matplotlib.pyplot as plt
import numpy as np

from extract_poem_features import getPoemModel
from poem_predict_rating import (getPoemScores, runPredictCV)
from extract_comment_features import (getAffectRatios,
    getAffectHistograms, getAverageCommentLength,
    getAverageAffectWordPerComment, getWordCountAffectCount,
    getLogAverageCommentLength)


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

def makePlots(xDict, yDict, filename="feature_scatter.jpg"):
    # xDict is a dict of dicts, the latter or which map feature to value
    print "Plotting %d feature plots..." % len(next(iter(xDict.values())))
    plt.figure(num=None, figsize=(24, 18), dpi=80, facecolor='w', edgecolor='k')
    for index, feature in enumerate(next(iter(xDict.values())).keys()):
        plt.subplot(5, 6, 1 + index)
        plotFeatureVsScore(xDict, yDict, feature)
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
    # # scatter plots
    # print "Extracting features..."
    # m = getPoemModel()
    # poems = m.poems
    # print "Finding y-values..."
    # # scores = getPoemScores() # plot voter scores
    # scores = getAffectRatios()  # plot affect ratios
    # # scores = getAverageCommentLength()  # plot average comment length
    # # scores = getAverageAffectWordPerComment()  
    # makePlots(poems, scores)
    # # blowUpPlots(poems, scores)

    # """
    # Experiment 0:
    # Identify correlation of features with aspect ratios. We can predict
    # this with about 30% reduction in error over the baseline.
    # """
    # m = getPoemModel()
    # poems = m.poems
    # scores = getAffectRatios()  # plot average comment length
    # # makePlots(poems, scores, "../experiments/exp00.jpg")
    # useFeatureList = ['posWords', 'conWords', 'typeTokenRatio','numWordsPerLine','perfectRhymeScore','proportionOfStops','proportionOfLiquids','negWords']
    # runPredictCV(poems, scores, useFeatureList)

    # """
    # Experiment 1:
    # Make scatter plot about comment length vs. affect ratio. This plot shows
    # that increasing comment length does result in a lower affect ratio.
    # However, if the change in affect ratio was caused by a change in comment
    # length, then we should be able to predict comment length.
    # """
    # x, y = zip(*getWordCountAffectCount())
    # plt.scatter(x, y)
    # plt.ylabel("affect ratio")
    # plt.xlabel("comment length (# words)")
    # plt.savefig("../experiments/exp01.jpg", format="jpg")

    # """
    # Experiment 2:
    # If comment length is the driver of affect ratio, we should find better
    # correlations with comment length. However, we cannot predict this very well.
    # """
    # m = getPoemModel()
    # poems = m.poems
    # scores = getAverageCommentLength()  # plot average comment length
    # # makePlots(poems, scores, "../experiments/exp02.jpg")
    # useFeatureList = ['posWords', 'conWords', 'typeTokenRatio','numWordsPerLine','perfectRhymeScore','proportionOfStops','proportionOfLiquids','negWords']
    # runPredictCV(poems, scores, useFeatureList)

    # """
    # Experiment 3:
    # We can predict log of average comment length with 10% reduction in error
    # over baseline (better than average comment length), but this is still worse
    # than predicting the affect ratio. Why?
    # """
    # m = getPoemModel()
    # poems = m.poems
    # scores = getLogAverageCommentLength()  # plot average comment length
    # # makePlots(poems, scores, "../experiments/exp02.jpg")
    # useFeatureList = ['posWords', 'conWords', 'typeTokenRatio','numWordsPerLine','perfectRhymeScore','proportionOfStops','proportionOfLiquids','negWords']
    # runPredictCV(poems, scores, useFeatureList)
