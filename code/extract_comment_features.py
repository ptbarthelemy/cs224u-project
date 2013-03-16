import sys
import re
import pickle
from os.path import isfile
from os import listdir, remove
from parse_realliwc import parseRealLIWC as liwc

MIN_COMMENT_NUM = 10
COMMENT_DIR = "../data/extracted_comments/"
AFFECT_RATIO_DICT = "affect_ratio.p"
NRC_CATEGORIES = ['anger', 'anticipation', 'disgust', 'fear', 'joy', 'sadness', 'surprise', 'trust']
NRC_FILE = '../data/NRC-lexicon.txt'


def getWords(text):
	return re.findall("[\w']+", text)

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

def getAffectRatios():
	if isfile(AFFECT_RATIO_DICT):
		print "Loading affect ratio dict from file..."
		return pickle.load(open(AFFECT_RATIO_DICT, "r"))

	print "Creating affect ratio dict..."
	affectRatios = {}
	affectWords = liwc()['Affect']
	for filename, text in getCommentSets(False).items():
		count = 0
		text = text[0]
		for regex in affectWords:
			count += len(re.findall(regex + r"\b", text))
		affectRatios[filename] = count * 1.0 / len(getWords(text))

	pickle.dump(affectRatios, open(AFFECT_RATIO_DICT, "w+"))
	return affectRatios

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

	print getAffectRatios()

	# m = getCommentSets()
	# print m['111'][0]
	# count = 0
	# for value in m.values():
	# 	count += len(value)
	# print count