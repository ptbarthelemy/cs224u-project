import sys
from extract_poem_features import PoemModel
from poem_predict_rating import getPoemScores
import matplotlib.pyplot as plt

def plotFeatureVsScore(poems, scores, feature):
    x = []
    y = []
    for key, value in poems.items():
        if scores.get(key, None) is None:
            continue
        x.append(value.get(feature))
        y.append(scores.get(key))

    plt.scatter(x, y)
    plt.xlabel(feature)
    plt.ylabel("score")

if __name__ == "__main__":
    dataFileName = "data.list"
    poemDirectory = sys.argv[1]
    metaDirectory = sys.argv[2]

    print "Extracting features..."
    poems = PoemModel(poemDirectory).poems

    print "Finding metadata info..."
    scores = getPoemScores(metaDirectory)

    print "Plotting %d feature plots..." %len(next(iter(poems.values())))
    plt.figure(num=None, figsize=(16, 12), dpi=80, facecolor='w', edgecolor='k')
    for index, feature in enumerate(next(iter(poems.values())).keys()):
        print index, feature
        plt.subplot(3, 4, 1 + index)
        plotFeatureVsScore(poems, scores, feature)
    # plt.show()
    plt.savefig("feature_scatter.pdf", format="pdf")

    # plt.figure(1)                # the first figure
    # plt.subplot(211)             # the first subplot in the first figure
    # plt.plot([1,2,3])
    # plt.subplot(212)             # the second subplot in the first figure
    # plt.plot([4,5,6])

    # plt.title('Easy as 1,2,3')   # subplot 211 title
    # plt.show()