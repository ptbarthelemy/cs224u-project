import sys
import re
import pickle
from os.path import isfile
from os import listdir, remove
from parse_realliwc import parseRealLIWC as liwc
from nltk import corpus

MIN_COMMENT_NUM = 10
COMMENT_DIR = "../data/extracted_comments/"
AFFECT_RATIO_DICT = "affect_ratio.p"
AFFECT_RATIO_PER_COMMENT_DICT = "affect_ratio2.p"
NRC_CATEGORIES = ['anger', 'anticipation', 'disgust', 'fear', 'joy', 'sadness', 'surprise', 'trust']
NRC_FILE = '../data/NRC-lexicon.txt'

stopwordList = corpus.stopwords.words('english')
affectWordList = liwc()['Affect']

def makeListRegex(l):
	result = r"\b" + r"\b|\b".join(l) + r"\b"
	return re.sub("\.", "[a-z]", result)

def removeStopwords(text):
	stopwordRegex = makeListRegex(stopwordList)
	return re.sub(stopwordRegex, "", text)

def getWords(text):
	return re.findall("[\w']+", removeStopwords(text))

def getCommentFilenames():
	return [(f, COMMENT_DIR + f) for f in listdir(COMMENT_DIR) if isfile(COMMENT_DIR + f)]

def cleanText(text):
	# nothing to clean
	return text

def getCommentsFromFile(path, commentAsDocument):
	comments = []
	f = open(path)
	text = cleanText(f.read().lower())
	f.close()

	comments = re.findall(r"commenter:[\w ]+\|\|\|   (.*)  \|\|\| likes", text)

	if len(comments) < MIN_COMMENT_NUM:
		return None
	if not commentAsDocument:
		return [' '.join(comments)]
	return comments

def getCommentSets(commentAsDocument=True):
	comments = {}
	for filename, path in getCommentFilenames():
		newComments = getCommentsFromFile(path, commentAsDocument)
		if newComments is not None:
			comments[filename] = newComments
	return comments

def getAffectRatio(text):
	count = 0
	words = getWords(text) # find words, filter out stopwords
	if len(words) == 0:
		return 0
	newText = ' '.join(words)
	affectWordRegex = makeListRegex(affectWordList)
	# print affectWordRegex
	# print "RE  :", re.findall(affectWordRegex, newText)
	return len(re.findall(affectWordRegex, newText)) * 1.0 / len(words)

def getAffectRatios():
	if isfile(AFFECT_RATIO_DICT):
		print "Loading affect ratio dict from file..."
		return pickle.load(open(AFFECT_RATIO_DICT, "r"))

	print "Creating affect ratio dict..."
	affectRatios = {}
	for filename, text in getCommentSets(False).items():
		affectRatios[filename] = getAffectRatio(text[0])

	pickle.dump(affectRatios, open(AFFECT_RATIO_DICT, "w+"))
	return affectRatios

def getTopAffectRatioComments():
	if isfile(AFFECT_RATIO_PER_COMMENT_DICT):
		print "Loading affect ratio dict from file..."
		comments = pickle.load(open(AFFECT_RATIO_PER_COMMENT_DICT, "r"))
	else:
		print "Calculating affect ratios..."
		comments = []
		for filename, text in getCommentSets(True).items():
			for comment in text:
				comments.append((getAffectRatio(comment), comment))
		pickle.dump(comments, open(AFFECT_RATIO_PER_COMMENT_DICT, "w+"))

	print "Sorting comments"
	comments = sorted(comments, key=lambda (x,y): -x)
	printNum = 20
	print "Highest affect ratios:"
	for i in range(printNum):
		print "%0.2f\t%s" % comments[i]
	print "Lowest affect ratios:"
	for i in range(printNum):
		print "%0.2f\t%s" % comments[-i-1]

	return comments

def getNRCLexicon():
	f = open(NRC_FILE)
	result = {}
	for line in f:
		if line.split()[2] == '0':
			continue
		word = line.split()[0]
		result[word] = result.get(word, [])
		result[word].append(line.split()[1])
	f.close()
	return result

def getAffectHistograms():
	affectHist = {}
	lexDict = getNRCLexicon()
	for filename, text in getCommentSets(False).items():
		# get counts
		hist = {}
		words = getWords(text[0])
		for word in words:
			cats = lexDict.get(word, None)
			if cats is not None:
				for cat in cats:
					hist[cat] = hist.get(cat, 0) + 1

		# normalize
		numWords = len(words)
		for cat, count in hist.items():
			hist[cat] = count * 1.0 / numWords

		# add to list
		affectHist[filename] = hist
	return affectHist

if __name__ == '__main__':

	# print getAffectRatios()
	m = getTopAffectRatioComments()

	# m = getCommentSets()
	# print m['111'][0]
	# count = 0
	# for value in m.values():
	# 	count += len(value)
	# print count