from extract_poem_features import getPoemModel
from poem_predict_rating import (getPoemScores, runPredictCV)
from extract_comment_features import (getAffectRatios,
    getAffectHistograms, getAverageCommentLength,
    getAverageAffectWordPerComment, getWordCountAffectCount,
    getLogAverageCommentLength, getNumberOfComments,
    getTopAffectRatioComments, getCommentTypeTokenRatio,
    getNRCRatios)
from make_plot import (makePlots)


def exp00():
    """
    Identify correlation of features with aspect ratios. We can predict
    this with about 30% reduction in error over the baseline.
    """
    m = getPoemModel()
    poems = m.poems
    scores = getAffectRatios()  # plot average comment length
    makePlots(poems, scores, "affect ratio", "../experiments/exp00.jpg")
    useFeatureList = ['posWords', 'conWords', 'typeTokenRatio','numWordsPerLine','perfectRhymeScore','proportionOfStops','proportionOfLiquids','negWords']
    runPredictCV(poems, scores, useFeatureList)

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
    plt.savefig("../experiments/exp01.jpg", format="jpg")

def exp011():
    """
    The relationship might be better represented with word count on a log
    scale. This plot shows that the two values are strongly correlated.
    """
    x, y = zip(*getWordCountAffectCount(True))
    plt.ylabel("affect ratio")
    plt.xlabel("comment length (# words)")
    _, pearP = pearsonr(x, y)
    label = "p < 0.0001" if pearP < 0.0001 else "p = %0.4f"%pearP    
    plt.scatter(x, y, label=label)
    plt.legend(loc=3)
    plt.savefig("../experiments/exp01.1.jpg", format="jpg")

def exp02():
    """
    If comment length is the driver of affect ratio, we should find better
    correlations with comment length. However, we cannot predict this very well.
    """
    m = getPoemModel()
    poems = m.poems
    scores = getAverageCommentLength()  # plot average comment length
    makePlots(poems, scores, "average comment length", "../experiments/exp02.jpg")
    useFeatureList = ['posWords', 'conWords', 'typeTokenRatio','numWordsPerLine','perfectRhymeScore','proportionOfStops','proportionOfLiquids','negWords']
    runPredictCV(poems, scores, useFeatureList)

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
    makePlots(poems, scores, "log of average comment length", "../experiments/exp03.jpg")
    useFeatureList = ['posWords', 'conWords', 'typeTokenRatio','numWordsPerLine','perfectRhymeScore','proportionOfStops','proportionOfLiquids','negWords']
    runPredictCV(poems, scores, useFeatureList)

def exp04():
    """
    Can we predict poem rating? No, it seems like we cannot predict it so well.
    """
    m = getPoemModel()
    poems = m.poems
    scores = getPoemScores()
    makePlots(poems, scores, "poem score", "../experiments/exp04.jpg")
    useFeatureList = ['posWords', 'conWords', 'typeTokenRatio','numWordsPerLine','perfectRhymeScore','proportionOfStops','proportionOfLiquids','negWords']
    runPredictCV(poems, scores, useFeatureList)

def exp05():
    """
    Can we predict the number of responses? Not so well.
    """
    m = getPoemModel()
    poems = m.poems
    scores = getNumberOfComments()
    makePlots(poems, scores, "number of comments", "../experiments/exp05.jpg")
    useFeatureList = ['posWords', 'conWords', 'typeTokenRatio','numWordsPerLine','perfectRhymeScore','proportionOfStops','proportionOfLiquids','negWords']
    runPredictCV(poems, scores, useFeatureList)

def exp06():
    """
    Can we predict the log of the number of responses? Not much better.
    """
    m = getPoemModel()
    poems = m.poems
    scores = getNumberOfComments(True) # use log
    makePlots(poems, scores, "log of number of comments", "../experiments/exp06.jpg")
    useFeatureList = ['posWords', 'conWords', 'typeTokenRatio','numWordsPerLine','perfectRhymeScore','proportionOfStops','proportionOfLiquids','negWords']
    runPredictCV(poems, scores, useFeatureList)

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
    makePlots(poems, scores, "comment type token ratio", "../experiments/exp08.jpg")
    useFeatureList = ['posWords', 'conWords', 'typeTokenRatio','numWordsPerLine','perfectRhymeScore','proportionOfStops','proportionOfLiquids','negWords']
    runPredictCV(poems, scores, useFeatureList)

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
    makePlots(poems, scores, "sampled type-token ratio", "../experiments/exp08.1.jpg")
    useFeatureList = ['posWords', 'conWords', 'typeTokenRatio','numWordsPerLine','perfectRhymeScore','proportionOfStops','proportionOfLiquids','negWords']
    runPredictCV(poems, scores, useFeatureList)

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
    makePlots(poems, scores, "NRC ratio", "../experiments/exp09.jpg")
    useFeatureList = ['posWords', 'conWords', 'typeTokenRatio','numWordsPerLine','perfectRhymeScore','proportionOfStops','proportionOfLiquids','negWords']
    runPredictCV(poems, scores, useFeatureList)


if __name__ == "__main__":
	exp09()
