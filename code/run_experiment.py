from extract_poem_features import getPoemModel
from poem_predict_rating import (getPoemScores, runPredictCV)
from extract_comment_features import (getAffectRatios,
    getAffectHistograms, getAverageCommentLength,
    getAverageAffectWordPerComment, getWordCountAffectCount,
    getLogAverageCommentLength, getNumberOfComments,
    getTopAffectRatioComments, getCommentTypeTokenRatio,
    getNRCRatios)
from make_plot import (makePlots, makeHistogram, plotArrays)
from scipy.stats.stats import pearsonr
import matplotlib.pyplot as plt

DEFAULT_FEATURE_LIST = ['HGI-positiv', 'HGI-concrete', 'typeTokenRatio',
    'NRC-joy', 'NRC-trust', 'perfectRhymeScore', 'NRC-anticipation',
    'proportionOfStops']

def exp00():
    """
    Identify correlation of features with aspect ratios. We can predict
    this with about 30% reduction in error over the baseline.
    """
    m = getPoemModel()
    poems = m.poems
    scores = getAffectRatios()  # plot average comment length
    makePlots(poems, scores, "affect ratio", "../experiments/exp00.pdf")
    runPredictCV(poems, scores, DEFAULT_FEATURE_LIST)

def exp01():
    """
    Experiment 1:
    Make scatter plot about comment length vs. affect ratio. This plot shows
    that increasing comment length does result in a lower affect ratio.
    However, if the change in affect ratio was caused by a change in comment
    length, then we should be able to predict comment length.
    """
    x, y = zip(*getWordCountAffectCount())
    plt.scatter(x, y)
    plt.ylabel("affect ratio")
    plt.xlabel("comment length (# words)")
    _, pearP = pearsonr(x, y)
    label = "p < 0.0001" if pearP < 0.0001 else "p = %0.4f"%pearP    
    plt.scatter(x, y, label=label)
    plt.legend(loc=3)
    plt.savefig("../experiments/exp01.pdf", format="pdf")

def exp011():
    """
    The relationship might be better represented with word count on a log
    scale. This plot shows that the two values are strongly correlated.
    """
    x, y = zip(*getWordCountAffectCount(True))
    plt.ylabel("affect ratio")
    plt.xlabel("comment length (log number of words)")
    _, pearP = pearsonr(x, y)
    plt.scatter(x, y, lw=0)
    plt.legend(loc=3)
    plt.savefig("../experiments/exp011.pdf", format="pdf")

def exp02():
    """
    If comment length is the driver of affect ratio, we should find better
    correlations with comment length. However, we cannot predict this very well.
    """
    m = getPoemModel()
    poems = m.poems
    scores = getAverageCommentLength()  # plot average comment length
    makePlots(poems, scores, "average comment length", "../experiments/exp02.pdf")
    runPredictCV(poems, scores, DEFAULT_FEATURE_LIST)

def exp03():
    """
    We can predict log of average comment length with 10% reduction in error
    over baseline (better than average comment length), but this is still worse
    than predicting the affect ratio. Why? Is there another descriptive feature
    of the comments that we can better describe?

    Are the comments with different affect ratios saying the same things
    differently or saying different things?
    """
    m = getPoemModel()
    poems = m.poems
    scores = getLogAverageCommentLength()
    makePlots(poems, scores, "log of average comment length", "../experiments/exp03.pdf")
    runPredictCV(poems, scores, DEFAULT_FEATURE_LIST)

def exp04():
    """
    Can we predict poem rating? No, it seems like we cannot predict it so well.
    """
    m = getPoemModel()
    poems = m.poems
    scores = getPoemScores()
    makePlots(poems, scores, "poem score", "../experiments/exp04.pdf")
    runPredictCV(poems, scores, DEFAULT_FEATURE_LIST)

def exp05():
    """
    Can we predict the number of responses? Not so well.
    """
    m = getPoemModel()
    poems = m.poems
    scores = getNumberOfComments()
    makePlots(poems, scores, "number of comments", "../experiments/exp05.pdf")
    runPredictCV(poems, scores, DEFAULT_FEATURE_LIST)

def exp06():
    """
    Can we predict the log of the number of responses? Not much better.
    """
    m = getPoemModel()
    poems = m.poems
    scores = getNumberOfComments(True) # use log
    makePlots(poems, scores, "log of number of comments", "../experiments/exp06.pdf")
    runPredictCV(poems, scores, DEFAULT_FEATURE_LIST)

def exp07():
    """
    What is the difference in the nature of comments with high and low affect
    ratios?

    high affect ratio implies:
    - shorter comments
    - less spanish
    - less analysis and observation and more unexplained praise and dispraise
        e.g. high: what beautiful use of words. lovely poem.
             high: you two are a couple of losers.
              low: christ's life is plausible. however, consider the theme of ambition: what it is; whether it is neutral or with the power to possess good or evil; and its source. then think to how 'we people on the pavement' took to a person whose skeletons were not on public display.
              low: this is poetic therapy at its very best. life-changing and liberating. i can't stop reading it...
        - how else can we describe these comments? is there a computational way to separate them?
            - length is of course a factor. what about semantics?
    """
    # getTopAffectRatioComments(20, 2000)
    # getTopAffectRatioComments(20, 3000)
    # getTopAffectRatioComments(20, 4000)
    getTopAffectRatioComments(20, 5000)

def exp08():
    """
    If high affect ratio comments are less rich in their analysis/observation,
    does this imply that they have a lower type-token ratio? Actually, this
    cannot be well predicted. (~0% reduction in accuracy)
    """
    m = getPoemModel()
    poems = m.poems
    scores = getCommentTypeTokenRatio()
    makePlots(poems, scores, "comment type token ratio", "../experiments/exp08.pdf")
    runPredictCV(poems, scores, DEFAULT_FEATURE_LIST)

def exp081():
    """
    Repeat exp 8, but sample from all of the words. This should control for the
    fact that longer documents tend to have lower type-token ratios. We can 
    predict this with ~15% reduction in error.

    This suggests that "richness" of response can be categorized by the type-
    token ratio, though this is not so easily predicted as affect ratio. With
    experiment 3, we know that we can predict the log of comment length with
    ~10% accuracy.

    Taking note of the sign of the correlation of each variable, this gives us
    a definition of 'richness' that includes:
        - longer comments
        - higher type-token ratio
        - lower affect ratio
    """
    m = getPoemModel()
    poems = m.poems
    scores = getCommentTypeTokenRatio(100) # sample words
    makePlots(poems, scores, "sampled type-token ratio", "../experiments/exp08.1.pdf")
    runPredictCV(poems, scores, DEFAULT_FEATURE_LIST)

def exp09():
    """
    Experiment 9:
    What is the difference in predicting the affect ratio with predicing the
    NRC ratio? Wouldn't this also capture emotion words? We cannot predict this
    as well. (Only ~3% over baseline.)
    """
    m = getPoemModel()
    poems = m.poems
    scores = getNRCRatios()
    makePlots(poems, scores, "NRC ratio", "../experiments/exp09.pdf")
    runPredictCV(poems, scores, DEFAULT_FEATURE_LIST)

def exp10():
    """
    Make the histogram of NRC words to show how all comments are similarly
    written.
    """
    affectHist = getAffectHistograms()
    makeHistogram(affectHist, "../experiments/exp10.pdf")

def getCorrelation(poems, scores, feature):
    x, y = [], []
    for key, value in poems.items():
        if scores.get(key, None) is None:
            continue
        if value.get(feature) is None:
            print feature
            assert False
        x.append(value.get(feature))
        y.append(scores.get(key))
    return pearsonr(x, y)

def exp11():
    poems = getPoemModel().poems
    scores = {}
    scores['affect'] = getAffectRatios()
    scores['cLength'] = getLogAverageCommentLength()
    scores['rating'] = getPoemScores()
    scores['typeToken'] = getCommentTypeTokenRatio(100)
    scores['numC'] = getNumberOfComments(True) # use log

    result = {}
    for k1, v1 in scores.items():
        for feature in poems.values()[0].keys():
            cor, p = getCorrelation(poems, v1, feature)
            if result.get(feature, None) is None:
                result[feature] = {k1:(cor, p)}
            else:
                result[feature][k1] = (cor, p)

    for k1 in sorted(result.keys(), key=lambda x:result[x]['rating'][1]): # sort by affect
        print "\\\\", k1, "& %0.2f & %0.4f" % result[k1]['affect'], "& %0.2f & %0.4f" % result[k1]['typeToken'] \
            , "& %0.2f & %0.4f" % result[k1]['cLength'], "& %0.2f & %0.4f" % result[k1]['rating'] \
            , "& %0.2f & %0.4f" % result[k1]['numC']

def checkCorrelation(dict1, dict2, xlabel, ylabel):
    x, y = [], []
    for key in dict1:
        if dict2.get(key, None) is None:
            continue
        x.append(dict1[key])
        y.append(dict2[key])
    return plotArrays(x, y, xlabel, ylabel)

def exp12():
    affect = getAffectRatios()
    cLength = getLogAverageCommentLength()
    typeToken = getCommentTypeTokenRatio(100)

    plt.figure(num=None, figsize=(18, 6), dpi=80, facecolor='w',
        edgecolor='k')

    plt.subplot(1, 3, 1)
    checkCorrelation(affect, cLength, "affect ratio", "log average comment length")
    plt.subplot(1, 3, 2)
    checkCorrelation(affect, typeToken, "affect ratio", "type-token ratio")
    plt.subplot(1, 3, 3)
    checkCorrelation(cLength, typeToken, "log average comment length", "type-token ratio")

    plt.savefig("../experiments/exp12.pdf", format="pdf")

if __name__ == "__main__":
	# exp00() # affect ratio
    # exp03() # log of average comment length
    # exp081() # aspect ratio
    # exp04() # rating
    # exp06() # log of number of comments
    # exp11()

    # exp07()
    exp12()
