import sys
import re
from os.path import isfile
from os import listdir, remove

def getFilesOf(dirname):
	return [dirname + f for f in listdir(dirname) if isfile(dirname + f)]

def isVowelPhoneme(phoneme):
	return phoneme[:1] in "aeiou"

class PoemModel():
	def __init__(self, dirname):
		self.dictionary = {}
		self.poems = []
		filenames = getFilesOf(dirname)
		self.rhymeDict = {}
		self.loadRhymeDict("../data/rhyme-dict.txt")

		for filename in filenames:
			# print "reading", filename
			text = open(filename).read()
			poemFeatures = []

			# add features
			self.getOrthographicFeatures(poemFeatures, text)
			self.getPoeticFeatures(poemFeatures, text)

			self.poems.append(poemFeatures)

	def loadRhymeDict(self, filename):
		f = open(filename, "r")
		for line in f.readlines():
			if line[:1] == ";": continue # skip comments
			line = line.lower()
			self.rhymeDict[line.split()[0]] = line.split()[1:]

		f.close()

		print "Rhyme of i and by", self.getWordRhymeScore("i", "by")
		# print "Rhyme of cat and hat", self.getWordRhymeScore("cat", "hat")
		# print "Rhyme of belt and melt", self.getWordRhymeScore("belt", "melt")
		# print "Rhyme of constipate and emancipate", self.getWordRhymeScore("constipate", "emancipate")

	def featureIndex(self, feature):
		result = self.dictionary.get(feature, None)
		if result is None:
			result = len(self.dictionary)
			self.dictionary[feature] = result
		return result

	def getOrthographicFeatures(self, poemFeatures, text):
		linesWithoutComments = list(a for a in text.split("\n") if a[:1] != "#")

		# number of lines
		numLines = len(list(a for a in linesWithoutComments if len(a) > 0)) # ignore empty lines
		# poemFeatures.append(self.featureIndex("numLines=%d" % numLines))

		# number of stanzas
		inStanza = True
		numStanzas = 1
		for i, line in enumerate(linesWithoutComments):
			if len(line.strip()) == 0 and i < len(linesWithoutComments) - 1: # some poems have trailing newline
				if inStanza:
					numStanzas += 1
					inStanza = False
			else:
				inStanza = True
		poemFeatures.append(self.featureIndex("numStanzas=%d" % numStanzas))
		poemFeatures.append(self.featureIndex("numLinesPerStanzas=%d" % (numLines/numStanzas)))

		# numWords per line
		words = re.findall(r"\w+", " ".join(linesWithoutComments))
		numWords = len(words)
		distinctWords = set(words)
		numDistinctWords = len(distinctWords)
		poemFeatures.append(self.featureIndex("numWordsPerLine=%d" % (numWords/numLines)))
		poemFeatures.append(self.featureIndex("typeTokenRatio=%d" % (numWords/numDistinctWords)))

	def getWordRhymeScore(self, w1, w2):
		p1, p2 = self.rhymeDict.get(w1.lower(), None), self.rhymeDict.get(w2.lower(), None)
		if p1 is None or p2 is None:
			return 0
		p1.reverse()
		p2.reverse()

		minNumPhoneme = min(len(p1), len(p2))
		rhymeScore = 0
		for i in range(minNumPhoneme):
			if p1[i] == p2[i]:
				rhymeScore += 1

		# return rhymeScore * 1.0 / minNumPhoneme # Tizhoosh uses this metric
		return rhymeScore

	def getPoemRhymeScore(self, text):
		trimLines = list(a for a in text.split("\n") if a[:1] != "#")
		lineWords = [a for a in [re.findall(r"\w+", line) for line in trimLines] if len(a) > 0]

		score = 0
		# print "\n\n"
		for i in range(len(lineWords)):
			# print lineWords[i]
			lineScore = 0
			if i > 0:
				lineScore = self.getWordRhymeScore(lineWords[i-1][-1], lineWords[i][-1])
				# print "compare", lineWords[i-1][-1], lineWords[i][-1], lineScore
			if i > 1:
				newLineScore = self.getWordRhymeScore(lineWords[i-2][-1], lineWords[i][-1])
				if newLineScore > lineScore:
					lineScore = newLineScore
				# print "compare", lineWords[i-2][-1], lineWords[i][-1], newLineScore
			# print lineScore
			score += lineScore
		return score * 1.0 / len(lineWords)

	def getPoeticFeatures(self, poemFeatures, text):
		poemFeatures.append("poemRhymeScore=%.1f" % self.getPoemRhymeScore(text))


if __name__ == "__main__":
	m = PoemModel("../data/extracted_poems/")
	# print m.poems
