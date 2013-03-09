import sys
import re
from os.path import isfile
from os import listdir, remove

def getFilesOf(path):
	if isfile(path):
		return [path]
	return [path + f for f in listdir(path) if isfile(path + f)]

def getWordsOf(filenames):
	result = {}
	for filename in filenames:
		f = open(filename)
		for line in f.readlines():
			for word in re.findall(r"[a-z]+", line.lower()):
				result[word] = result.get(word, 0) + 1
		f.close()
	return result

if __name__ == "__main__":
	positiveWords = set(getWordsOf(["../data/wordlists/LoughranMcDonald_Positive.csv"]).keys())
	negativeWords = set(getWordsOf(["../data/wordlists/LoughranMcDonald_Negative.csv"]).keys())
	wordsInPoems = getWordsOf(getFilesOf("../data/extracted_comments/"))

	count = 0
	for word, freq in sorted(wordsInPoems.items(), key=lambda (x,y): -y):
		if word not in positiveWords and word not in negativeWords:
			continue
		print word, ",", freq, ",", word in positiveWords
		count += 1
		if count > 20:
			break