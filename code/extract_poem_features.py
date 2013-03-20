"""
This module reads the poems and extracts the features, storing them in a 
PoemModel object. To obtain a dictionary of these features (maps filename
	to features, e.g. "011" : {feature dict}), use poemModel.poems.
"""

import sys
import re
import pickle
import nrc_intensity
from os.path import isfile
from os import listdir, remove
from math import log
from parse_realliwc import parseRealLIWC as liwc

# up to how many words back are we looking to find alliteration?
WORDS_FOR_ALLITERATION = 5
# up to how many lines back are we looking for rhyme?
LINES_FOR_RHYME = 2
POEM_DIR = "../data/extracted_poems/"
RHYME_DICT_PATH = "../data/rhyme-dict.txt"
HGI_PATH = "../data/wordlists/harvard-general-inquirer-basic.csv"
SAVED_MODEL = "poem_model.p"
NASALS = set(['M','EM','N','EN','NG','ENG'])
LIQUIDS = set(['L','EL','R','DX','NX'])
SEMIVOWELS = set(['Y','W','Q']) # all nasals, liquids, and semivowels
FRICATIVES = set(['F','V','TH','DH','S','Z','SH','ZH','HH','CH','JH']) # all fricatives and affricates
STOPS = set(['P','B','T','D','K','G'])


def getWords(text):
	return re.findall("[\w']+", text)

def getLines(text):
	return text.split("\n")

def getFilesOf(dirname):
	return [dirname + f for f in listdir(dirname) if isfile(dirname + f)]

def poemNotPublished(text):
	# Some of our poems are actually not provided. Don't use these!
	if "The text of this poem could not be published because of Copyright laws" in text:
		return True
	return False

def isVowelPhoneme(phoneme):
	# Check to see whether the phoneme starts with a vowel. This means that
	# it is a vowel sound.
	return phoneme[:1] in "aeiou"

def cleanPoem(text):
	if poemNotPublished(text):
		# skip unpublished poem
		return None
	result = re.sub("#.*\n", "", text) # remove comments
	result = result.lower() # make lowercase
	return result

def getPoemModel():
	if isfile(SAVED_MODEL):
		print "Loading poem features from file..."
		return pickle.load(open(SAVED_MODEL, "r"))

	print "Creating poem features..."
	pm = PoemModel()
	pickle.dump(pm, open(SAVED_MODEL, "w+"))
	return pm

class PoemModel():
	def __init__(self):
		self.poems = {}
		filenames = getFilesOf(POEM_DIR)
		self.rhymeDict = {}
		self.loadRhymeDict(RHYME_DICT_PATH)
		self.loadWordsFromHGI(HGI_PATH)

		for filename in filenames:
			# read poem / clean poem
			text = cleanPoem(open(filename).read())
			if not text:
				continue

			# add features
			poemFeatures = {}
			filename = filename.split("/")[-1]
			# self.getAffectRatio(poemFeatures, text) # not sure whether we want this
			self.getOrthographicFeatures(poemFeatures, text)
			self.getPoeticFeatures(poemFeatures, text)
			self.getSentimentFeatures(poemFeatures, text)
			self.poems[filename] = poemFeatures

	def getAffectRatio(self, filename, text):
		# this could be provided as a feature, too
		self.wordsAffect = liwc()['Affect']
		count = 0
		for regex in self.wordsAffect:
			count += len(re.findall(regex + r"\b", text))
		poemFeatures["affectRatio"] = count * 1.0 / len(getWords(text))

	def loadWordsFromHGI(self, filename):
		# Load words from Harvard General inquirer based on the categories
		# specified below.
		positiveCategories = ["positiv"]
		negativeCategories = ["negativ"]
		abstractCategories = ["abs@", "abs"]
		concreteCategories = ["space", "object", "color", "place"]

		self.wordsPositive, self.wordsNegative, self.wordsAbstract, \
			self.wordsConcrete = [set() for i in range(4)]

		f = open(filename, "r")
		for line in f.readlines()[1:]:
			cols = line.lower().split(",")
			word = cols[0].split("#")[0]
			for cat in cols[1:]:
				if cat in abstractCategories:
					self.wordsAbstract.add(word)
				elif cat in concreteCategories:
					self.wordsConcrete.add(word)
				if cat in positiveCategories:
					self.wordsPositive.add(word)
				elif cat in negativeCategories:
					self.wordsNegative.add(word)
		f.close()

	def loadRhymeDict(self, filename):
		# Load the CMU rhyming dictionary. Store as a dictionary.
		f = open(filename, "r")
		for line in f.readlines():
			if line[:1] == ";": continue # skip comments
			line = line.lower()
			self.rhymeDict[line.split()[0]] = line.split()[1:]
		f.close()

	def getOrthographicFeatures(self, poemFeatures, text):
		lines = getLines(text)

		# number of lines
		numLines = len(list(a for a in lines if len(a) > 0)) # ignore empty lines

		# number of stanzas
		inStanza = True
		numStanzas = 1
		for i, line in enumerate(lines):
			if len(line.strip()) == 0 and i < len(lines) - 1: # some poems have trailing newline
				if inStanza:
					numStanzas += 1
					inStanza = False
			else:
				inStanza = True

		# numWords per line
		words = re.findall(r"\w+", " ".join(lines))
		numWords = len(words)
		distinctWords = set(words)
		numDistinctWords = len(distinctWords)

		poemFeatures["numLines"] = log(numLines)
		poemFeatures["numStanzas"] = log(numStanzas)
		poemFeatures["numLinesPerStanzas"] = (numLines * 1.0 /numStanzas)
		poemFeatures["numWordsPerLine"] = numWords * 1.0 / numLines
		poemFeatures["typeTokenRatio"] = numDistinctWords * 1.0 / numWords

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

		phonemes = self.rhymeDict.get(word, None)
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
		p1 = self.rhymeDict.get(w1, None)
		p2 = self.rhymeDict.get(w2, None)
		if p1 is None or p2 is None: return 0

		p1 = p1[0]
		p2 = p2[0]

		if p1 == p2 and not isVowelPhoneme(p1):
			return 1
		return 0

	def getPoemRhyme(self, text):
		lineWords = [getWords(line) for line in getLines(text) if len(getLines(text)) > 0]
		lineWords = [a for a in [re.findall(r"\w+", line) for line in \
			text.split("\n")] if len(a) > 0]

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
		words = getWords(text)
		score = 0
		for i in range(len(words)):
			for j in range(min(WORDS_FOR_ALLITERATION, i)):
				if self.isAlliteration(words[i], words[i - 1 - j]):
					score += 1
					break

		# normalize by all words in text
		return score * 1.0 / len(words)

	def countPhonemes(self, text, phonemeSet):
		words = getWords(text)
		score = 0
		total_phonemes = 0
		for i in range(len(words)):
			phonemes = self.rhymeDict.get(words[i],None)
			if phonemes != None:
				total_phonemes += len(phonemes)
				for phon in phonemes:
					if phon.upper() in phonemeSet:
						score += 1
      	
      	# normalize by all words in text
		return score * 1.0 / total_phonemes

	def getPoeticFeatures(self, poemFeatures, text):
		perfectRhyme, slantRhyme = self.getPoemRhyme(text)
		poemFeatures["perfectRhymeScore"] = perfectRhyme
		poemFeatures["slantRhymeScore"] = slantRhyme
		poemFeatures["alliterationScore"] = self.getPoemAllitScore(text)
		poemFeatures["proportionOfNasals"] = self.countPhonemes(text,NASALS)
		poemFeatures["proportionOfFricatives"] = self.countPhonemes(text,FRICATIVES)
		poemFeatures["proportionOfStops"] = self.countPhonemes(text,STOPS)
		poemFeatures["proportionOfLiquids"] = self.countPhonemes(text,LIQUIDS)


	def getSentimentFeatures(self, poemFeatures, text):
		words = getWords(text)	
		cate = nrc_intensity.processNrcWords()
		
		posWords, negWords, conWords, absWords = [0] * 4
		anger, anticipation, disgust, fear, joy, neg, pos, sadness, surprise, trust = [0] * 10
		for word in words:
			if word in self.wordsPositive:
				posWords += 1
			elif word in self.wordsNegative:
				negWords += 1
			if word in self.wordsAbstract:
				absWords += 1
			elif word in self.wordsConcrete:
				conWords += 1
			if word in cate['anger']:
			  anger += cate['anger'][word]
			if word in cate['anticipation']:
			  anticipation += cate['anticipation'][word]
			if word in cate['disgust']:
			  disgust += cate['disgust'][word]
			if word in cate['fear']:
			  fear += cate['fear'][word]
			if word in cate['joy']:
			  joy += cate['joy'][word]
			if word in cate['sadness']:
			  sadness += cate['sadness'][word]
			if word in cate['surprise']:
			  surprise += cate['surprise'][word]
			if word in cate['trust']:
			  trust += cate['trust'][word]
			if word in cate['positive']:
			  pos += cate['positive'][word]
			if word in cate['negative']:
			  neg += cate['negative'][word]

		poemFeatures["HGI-positiv"] = posWords * 1.0 / len(words)
		poemFeatures["HGI-negativ"] = negWords * 1.0 / len(words)
		poemFeatures["HGI-concrete"] = conWords * 1.0 / len(words)
		poemFeatures["HGI-abstract"] = absWords * 1.0 / len(words)
		poemFeatures["NRC-anger"] = anger / len(words)
		poemFeatures["NRC-anticipation"] = anticipation / len(words)
		poemFeatures["NRC-fear"] = fear / len(words)
		poemFeatures["NRC-joy"] = joy / len(words)
		poemFeatures["NRC-sadness"] = sadness / len(words)
		poemFeatures["NRC-surprise"] = surprise / len(words)
		poemFeatures["NRC-trust"] = trust / len(words)
		poemFeatures["NRC-disgust"] = disgust / len(words)


if __name__ == "__main__":
	m = getPoemModel()
	
	print m.isPerfectRhyme("lamentable", "preventable")
	print m.isSlantRhyme("lamentable", "preventable")
