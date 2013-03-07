import sys
import re
from os.path import isfile
from os import listdir, remove
# from sklearn.feature_extraction import DictVectorizer

# up to how many words back are we looking to find alliteration?
WORDS_FOR_ALLITERATION = 5

# up to how many lines back are we looking for rhyme?
LINES_FOR_RHYME = 2


def getFilesOf(dirname):
	return [dirname + f for f in listdir(dirname) if isfile(dirname + f)]

def isVowelPhoneme(phoneme):
	return phoneme[:1] in "aeiou"

def loadWords(filename, wordSet):
	f = open(filename)
	for line in f.readlines():
		wordSet.add(line.split(",")[0].lower())
	f.close()

class PoemModel():
	def __init__(self, dirname):
		self.poems = []
		filenames = getFilesOf(dirname)
		self.rhymeDict = {}
		self.wordsPositive = set()
		self.wordsNegative = set()
		self.loadRhymeDict("../data/rhyme-dict.txt")
		loadWords("../data/wordlists/LoughranMcDonald_Positive.csv", self.wordsPositive)
		loadWords("../data/wordlists/LoughranMcDonald_Negative.csv", self.wordsNegative)
		self.loadWordsFromHGI("../data/wordlists/harvard-general-inquirer-basic.csv")

		for filename in filenames:
			# print "reading", filename
			text = open(filename).read()
			poemFeatures = {}

			# add features
			self.getOrthographicFeatures(poemFeatures, text)
			self.getPoeticFeatures(poemFeatures, text)
			self.getPoeticFeatures(poemFeatures, text)
			self.getSentimentFeatures(poemFeatures, text)

			self.poems.append(poemFeatures)

	def loadWordsFromHGI(self, filename):
		abstractCategories = ["abs@", "abs"]
		concreteCategories = ["space", "object", "color", "place"]

		self.wordsAbstract = set()
		self.wordsConcrete = set()

		f = open(filename, "r")
		for line in f.readlines()[1:]:
			cols = line.lower().split(",")
			word = cols[0].split("#")[0]
			for cat in cols[1:]:
				if cat in abstractCategories:
					self.wordsAbstract.add(word)
				elif cat in concreteCategories:
					self.wordsConcrete.add(word)
		f.close()

	def loadRhymeDict(self, filename):
		f = open(filename, "r")
		for line in f.readlines():
			if line[:1] == ";": continue # skip comments
			line = line.lower()
			self.rhymeDict[line.split()[0]] = line.split()[1:]
		f.close()

	def getOrthographicFeatures(self, poemFeatures, text):
		linesWithoutComments = list(a for a in text.split("\n") if a[:1] != "#")

		# number of lines
		numLines = len(list(a for a in linesWithoutComments if len(a) > 0)) # ignore empty lines
		poemFeatures["numLines"] = numLines

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
		poemFeatures["numStanzas"] = numStanzas
		poemFeatures["numLinesPerStanzas"] = (numLines * 1.0 /numStanzas)

		# numWords per line
		words = re.findall(r"\w+", " ".join(linesWithoutComments))
		numWords = len(words)
		distinctWords = set(words)
		numDistinctWords = len(distinctWords)
		poemFeatures["numWordsPerLine"] = numWords * 1.0 / numLines
		poemFeatures["typeTokenRatio"] = numWords * 1.0 / numDistinctWords

	def scanPhonemes(self, phonemes, plist, i, stopatVowel=True):
		while i < len(phonemes):
			if isVowelPhoneme(phonemes[i]) == stopatVowel: break
			plist.append(phonemes[i])
			i += 1
		return i 

	def rhymePieces(self, word):
		cm1 = [] # consonant-minus-1  e.g. [Z] from "skies"
		vm1 = [] # vowel-minus-1      e.g. [AY1] from "skies"
		cm2 = [] # consonant-minus-2  e.g. [S, K] from "skies"

		phonemes = self.rhymeDict.get(word.lower(), None)
		if phonemes is None:
			return None, None, None
		phonemes = phonemes[::-1]

		i = self.scanPhonemes(phonemes, cm1, 0, True)
		i = self.scanPhonemes(phonemes, vm1, i, False)
		i = self.scanPhonemes(phonemes, cm2, i, True)

		return cm2, vm1, cm1

	def isPerfectRhyme(self, w1, w2):
		"""
		Per Wikipedia, perfect rhyme is defined as having the same vowel sound,
		but having a different consonant preceding this vowel sound. So:
			- consonants after the vowel sound must match
			- vowel sound must match
			- consonant sounds before the vowel cannot match
		"""
		cm2_1, vm1_1, cm1_1 = self.rhymePieces(w1)
		cm2_2, vm1_2, cm1_2 = self.rhymePieces(w2)

		if cm2_1 != cm2_2 and vm1_1 == vm1_2 and cm1_1 == cm1_2 \
			and len(vm1_1) > 0:
			return 1
		return 0

	def isSlantRhyme(self, w1, w2):
		"""
		Per Wikipedia, slant rhyme shares the same consonant sound but has
		different vowel sound.
		"""
		cm2_1, vm1_1, cm1_1 = self.rhymePieces(w1)
		cm2_2, vm1_2, cm1_2 = self.rhymePieces(w2)

		if vm1_1 != vm1_2 and cm1_1 == cm1_2 and len(cm1_1) > 0:
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
		text = re.sub(r"^#.*\n", "",text.lower()) # remove comments
		words = re.findall(r"\w+", text)
		score = 0
		for i in range(len(words)):
			for j in range(min(WORDS_FOR_ALLITERATION, i)):
				score += self.isAlliteration(words[i], words[i - 1 - j])

		# normalize by all words in text
		return score * 1.0 / len(words)

	def getPoeticFeatures(self, poemFeatures, text):
		perfectRhyme, slantRhyme = self.getPoemRhyme(text)
		poemFeatures["perfectRhymeScore"] = perfectRhyme
		poemFeatures["slantRhymeScore"] = slantRhyme
		poemFeatures["alliterationScore"] = self.getPoemAllitScore(text)


	def getSentimentFeatures(self, poemFeatures, text):
		text = re.sub(r"^#.*\n", "",text.lower()) # remove comments
		words = re.findall(r"\w+", text)

		posWords = 0
		negWords = 0
		conWords = 0
		absWords = 0
		for word in words:
			if word in self.wordsPositive:
				posWords += 1
			elif word in self.wordsNegative:
				negWords += 1
			if word in self.wordsAbstract:
				absWords += 1
			elif word in self.wordsConcrete:
				conWords += 1

		poemFeatures["posWords"] = posWords * 1.0 / len(words)
		poemFeatures["negWords"] = negWords * 1.0 / len(words)
		poemFeatures["conWords"] = conWords * 1.0 / len(words)
		poemFeatures["absWords"] = absWords * 1.0 / len(words)

if __name__ == "__main__":
	m = PoemModel("../data/extracted_poems/")
	print m.poems[-1]
	# vec = DictVectorizer()
	# print vec.fit_transform(m.poems).toarray()
	# print vec.get_feature_names()
	# print m.poems

