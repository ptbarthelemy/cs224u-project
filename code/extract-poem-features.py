import sys
import re
from os.path import isfile
from os import listdir, remove

# up to how many words back are we looking to find alliteration?
WORDS_FOR_ALLITERATION = 5

# up to how many lines back are we looking for rhyme?
LINES_FOR_RHYME = 2


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

	# def getWordRhymeScore(self, w1, w2):
	# 	p1, p2 = self.rhymeDict.get(w1.lower(), None), self.rhymeDict.get(w2.lower(), None)
	# 	if p1 is None or p2 is None: return 0
	# 	p1 = p1[::-1]
	# 	p2 = p2[::-1]

	# 	minNumPhoneme = min(len(p1), len(p2))
	# 	rhymeScore = 0
	# 	for i in range(minNumPhoneme):
	# 		if p1[i] == p2[i]:
	# 			rhymeScore += 1

	# 	# return rhymeScore * 1.0 / minNumPhoneme # Tizhoosh uses this metric
	# 	return rhymeScore

	def wordRhymeScheme(self, word):
		cm1 = [] # consonant-minus-1, e.g. [Z] from "skies"
		vm1 = [] # vowel-minus-1, e.g. [AY1] from "skies"
		cm2 = [] # consonant-minus-2, e.g. [S, K] from "skies"

		phonemes = self.rhymeDict.get(word.lower(), None)
		if phonemes is None:
			return None, None, None
		phonemes = phonemes[::-1]

		i = 0
		while i < len(phonemes):
			if isVowelPhoneme(phonemes[i]):
				break
			cm1.append(phonemes[i])
			i += 1

		while i < len(phonemes):
			if not isVowelPhoneme(phonemes[i]):
				break
			vm1.append(phonemes[i])
			i += 1

		while i < len(phonemes):
			if isVowelPhoneme(phonemes[i]):
				break
			cm2.append(phonemes[i])
			i += 1

		return cm2, vm1, cm1

	def isPerfectRhyme(self, w1, w2):
		"""
		Per Wikipedia, perfect rhyme is defined as having the same vowel sound,
		but having a different consonant preceding this vowel sound. So:
			- consonants after the vowel sound must match
			- vowel sound must match
			- consonant sounds before the vowel cannot match
		"""
		cm2_1, vm1_1, cm1_1 = self.wordRhymeScheme(w1)
		cm2_2, vm1_2, cm1_2 = self.wordRhymeScheme(w2)

		if cm2_1 is None and vm1_1 is None and cm1_1 is None:
			return 0
		if cm2_1 != cm2_2 and vm1_1 == vm1_2 and cm1_1 == cm1_2:
			print w1, w2, "perfect rhyme"
			return 1
		return 0


	def isSlantRhyme(self, w1, w2):
		"""
		Per Wikipedia, slant rhyme shares the same consonant sound but has
		different vowel sound.
		"""
		cm2_1, vm1_1, cm1_1 = self.wordRhymeScheme(w1)
		cm2_2, vm1_2, cm1_2 = self.wordRhymeScheme(w2)

		if cm2_1 is None and vm1_1 is None and cm1_1 is None:
			return 0
		if vm1_1 != vm1_2 and cm1_1 == cm1_2:
			print w1, w2, "slant rhyme"
			return 1
		return 0

	def isAlliteration(self, w1, w2):
		"""
		Per Kao and Jurafsky, alliteration means having the same consonant sound
		at the beginning of a word. I think more generally, alliteration needs
		to occur at the beginning of a stressed syllable, so it could occur
		within a word.
		"""
		p1 = self.rhymeDict.get(w1.lower(), None)
		p2 = self.rhymeDict.get(w2.lower(), None)
		if p1 is None or p2 is None: return 0

		p1 = p1[0]
		p2 = p2[0]

		if p1 == p2 and not isVowelPhoneme(p1):
			return 1
		return 0

	def getPoemRhyme(self, text):
		trimLines = list(a for a in text.split("\n") if a[:1] != "#")
		lineWords = [a for a in [re.findall(r"\w+", line) for line in trimLines] if len(a) > 0]

		perfectRhyme = 0
		slantRhyme = 0
		for i in range(len(lineWords)):
			pLineScore = 0
			sLineScore = 0
			for j in range(min(LINES_FOR_RHYME, i)):
				pLineScore = max(pLineScore, self.isPerfectRhyme(lineWords[i - 1 - j][-1], lineWords[i][-1]))
				sLineScore = max(sLineScore, self.isSlantRhyme(lineWords[i - 1 - j][-1], lineWords[i][-1]))
			perfectRhyme += pLineScore
			slantRhyme += sLineScore

		# normalize by number of lines
		return perfectRhyme * 1.0 / len(lineWords), slantRhyme * 1.0 / len(lineWords)

	def getPoemAllitScore(self, text):
		text = re.sub(r"^#.*\n", "",text.lower())
		words = re.findall(r"\w+", text)
		score = 0
		for i in range(len(words)):
			for j in range(min(WORDS_FOR_ALLITERATION, i)):
				score += self.isAlliteration(words[i], words[i - 1 - j])

		# normalize by all words in text
		return score * 1.0 / len(words)

	def getPoeticFeatures(self, poemFeatures, text):
		perfectRhyme, slantRhyme = self.getPoemRhyme(text)
		poemFeatures.append("perfectRhymeScore=%.1f" % perfectRhyme)
		poemFeatures.append("slantRhymeScore=%.1f" % perfectRhyme)
		poemFeatures.append("alliterationScore=%.1f" % self.getPoemAllitScore(text))

if __name__ == "__main__":
	m = PoemModel("../data/extracted_poems/")
	# print m.poems
