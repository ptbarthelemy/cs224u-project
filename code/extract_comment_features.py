import sys
import re
import pickle
from os.path import isfile
from os import listdir, remove
from parse_realliwc import parseRealLIWC as liwc
from nltk import corpus
from math import log
from random import sample

MIN_COMMENT_NUM = 10
COMMENT_DIR = "../data/extracted_comments/"
AFFECT_RATIO_DICT = "affect_ratio.p"
AFFECT_RATIO_PER_COMMENT_DICT = "affect_ratio2.p"
NRC_RATIO_DICT = "nrc_ratio.p"
NRC_FILE = '../data/NRC-lexicon.txt'
IGNORE_FILES = ["039", # someone added wikipedia articles as comments
		"411", "447","466" # lots of loves
	]

stopwordList = corpus.stopwords.words('english')
affectWordList = liwc()['Affect']

def makeRegexFromList(l):
	result = r"\b" + r"\b|\b".join(l) + r"\b"
	return re.sub("\.", "[a-z]", result)

def removeStopwords(text):
	stopwordRegex = makeRegexFromList(stopwordList)
	return re.sub(stopwordRegex, "", text)

def getWords(text):
	return re.findall("[\w']+", removeStopwords(text))

def getCommentFilenames():
	return [(f, COMMENT_DIR + f) for f in listdir(COMMENT_DIR) if isfile(COMMENT_DIR + f)]

def cleanData(filename, text):
	# nothing to clean
	if filename in IGNORE_FILES:
		return ""
	return text

def getCommentsFromFile(filename, path, commentAsDocument):
	comments = []
	f = open(path)
	text = cleanData(filename, f.read().lower())
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
		newComments = getCommentsFromFile(filename, path, commentAsDocument)
		if newComments is not None:
			comments[filename] = newComments
	return comments

def getAverageCommentLength():
	result = {}
	for filename, text in getCommentSets(True).items():
		average = sum([len(getWords(a)) for a in text]) * 1.0 / len(text)
		result[filename] = average
	return result

def getLogAverageCommentLength():
	result = {}
	for filename, text in getCommentSets(True).items():
		average = sum([len(getWords(a)) for a in text]) * 1.0 / len(text)
		result[filename] = log(average)
	return result

def getAverageAffectWordPerComment():
	result = {}
	for filename, text in getCommentSets(True).items():
		average = sum([len(re.findall(makeRegexFromList(affectWordList), ' '.join(getWords(a)))
			) for a in text]) * 1.0 / len(text)
		result[filename] = average
	return result

def getNumberOfComments(useLog=False):
	result = {}
	for filename, text in getCommentSets(True).items():
		result[filename] = len(text) if not useLog else log(len(text))
	return result

def getCommentTypeTokenRatio(sampling=0):
	result = {}
	skipcount = 0
	for filename, text in getCommentSets(False).items():
		words = getWords(text[0])
		if sampling > 0:
			if len(words) < sampling:
				skipcount += 1
				continue
			words = sample(words, sampling)
			result[filename] = len(set(words)) * 1.0 / len(words)
		else:
			numTokens = len(words)
			if numTokens == 0:
				skipcount += 1
				continue
			numTypes = len(set(words))
			result[filename] = numTypes * 1.0 / numTokens
	print "Skipped %d files due to insufficient commentary." % skipcount
	return result

def getWordCountAffectCount(useLog=False):
	result = []
	for filename, text in getCommentSets(True).items():
		for comment in text:
			words = getWords(comment)
			numWords = len(words)
			if numWords == 0:
				continue
			numAffectWords = len(re.findall(makeRegexFromList(affectWordList), ' '.join(words))) * 1.0 / numWords
			if useLog:
				numWords = log(numWords)
			result.append((numWords, numAffectWords))
	return result

def getWordRatio(text, wordlist):
	count = 0
	words = getWords(text) # find words, filter out stopwords
	if len(words) == 0:
		return 0
	newText = ' '.join(words)
	regex = makeRegexFromList(wordlist)
	return len(re.findall(regex, newText)) * 100.0 / len(words)

def getAffectRatios():
	if isfile(AFFECT_RATIO_DICT):
		print "Loading affect ratio dict from file..."
		return pickle.load(open(AFFECT_RATIO_DICT, "r"))

	print "Creating affect ratio dict..."
	affectRatios = {}
	for filename, text in getCommentSets(False).items():
		affectRatios[filename] = getWordRatio(text[0], affectWordList)

	pickle.dump(affectRatios, open(AFFECT_RATIO_DICT, "w+"))
	return affectRatios

def getNRCRatios():
	if isfile(NRC_RATIO_DICT):
		print "Loading affect ratio dict from file..."
		return pickle.load(open(NRC_RATIO_DICT, "r"))

	print "Creating NRC ratio dict..."
	result = {}
	for filename, text in getCommentSets(False).items():
		result[filename] = getNRCRatio(text[0], getNRCLexicon().keys())

	pickle.dump(result, open(NRC_RATIO_DICT, "w+"))
	return result

def getTopAffectRatioComments(printNum, burnIn):
	if isfile(AFFECT_RATIO_PER_COMMENT_DICT):
		print "Loading affect ratio dict from file..."
		comments = pickle.load(open(AFFECT_RATIO_PER_COMMENT_DICT, "r"))
	else:
		print "Calculating affect ratios..."
		comments = []
		for filename, text in getCommentSets(True).items():
			for comment in text:
				comments.append((getAffectRatio(comment), comment, re.findall(makeRegexFromList(affectWordList), ' '.join(getWords(comment)))))
		pickle.dump(comments, open(AFFECT_RATIO_PER_COMMENT_DICT, "w+"))

	print "Sorting comments"
	comments = sorted(comments, key=lambda (x,y,z): -x)
	print "\nHigher affect ratios:"
	for i in range(printNum):
		print comments[i + burnIn]
	print "\nLower affect ratios:"
	for i in range(printNum):
		print comments[-i-1 - burnIn]

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
	getTopAffectRatioComments(20, 1000)
