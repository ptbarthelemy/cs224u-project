import sys
import re
import pickle
from os.path import isfile
from os import listdir, remove
from parse_realliwc import parseRealLIWC as liwc

MIN_COMMENT_NUM = 10
COMMENT_DIR = "../data/extracted_comments/"
AFFECT_RATIO_DICT = "affect_ratio.p"

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
	commentSets = getCommentSets(False)
	affectRatios = {}
	affectWords = liwc()['Affect']
	for filename, text in commentSets.items():
		count = 0
		text = text[0]
		for regex in affectWords:
			count += len(re.findall(regex + r"\b", text))
		affectRatios[filename] = count * 1.0 / len(getWords(text))

	pickle.dump(affectRatios, open(AFFECT_RATIO_DICT, "w+"))
	return affectRatios

if __name__ == '__main__':

	print getAffectRatios()

	# m = getCommentSets()
	# print m['111'][0]
	# count = 0
	# for value in m.values():
	# 	count += len(value)
	# print count