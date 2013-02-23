import sys
import re
from os.path import isfile
from os import listdir, remove
from gensim import corpora, models, similarities

STOPWORDS = set(['for', 'a', 'of', 'the', 'and', 'to', 'in', 
	'i', 'is', 'it', 'you', 'we', 'that', 'this', 's', 'as',
	'but', 'not', 'so', 'my', 'your'])

def getFilesOf(dirname):
	return [dirname + f for f in listdir(dirname) if isfile(dirname + f)]

def getWordlist(filenames):
	wordlist = set()
	for filename in filenames:
		f = open(filename)
		for line in f.readlines():
			wordlist.add(line.split(",")[0].lower())
		f.close()
	return wordlist

def cleanComments(text):
	return re.sub(r"\* \[ \!\[share on facebook\].*[pa]m\)", "", text)

def extractComments(filenames):
	print "Reading files..."
	comments = []
	for filename in filenames:
		f = open(filename)
		# treat each comment as one document
		text = f.read().lower()
		text = cleanComments(text)
		comments.extend(re.findall(r"commenter:[\w ]+\|\|\|  (.*)  \|\|\| likes", text))

		# # treat all comments for one poem as one document
		# addComment = ""
		# text = f.read()
		# text = cleanComments(text)
		# for comment in re.findall(r"Commenter:[\w ]+\|\|\|  (.*)  \|\|\| likes", text):
		# 	addComment += comment
		# print ">>>NEW COMMENT: ", addComment[:200]
		# comments.append(addComment)

		f.close()
	return comments

	# # use poems instead
	# result = []
	# for filename in getFilesOf("../data/extracted_poems/"):
	# 	f = open(filename)
	# 	text = f.read().lower()
	# 	result.append(text)
	# 	f.close()
	# return result

def tokenize(documents, wordlist=set()):
	# remove stop words (optional?)
	print "Cleaning comments..."
	texts = [[word for word in re.findall("[A-Za-z]+", document)
		if word not in STOPWORDS and (word in wordlist or len(wordlist) == 0)]
		for document in documents]

	# remove words that appear only once
	print "Removing words that appear only once..."
	all_tokens = sum(texts, [])
	counts = {}
	for t in all_tokens:
		counts[t] = counts.get(t, 0) + 1
	tokens_once = set(t for t in counts.keys() if counts.get(t) == 1)
	texts = [[word for word in text if word not in tokens_once]
		for text in texts]

	return texts

def createVSM(documents, dictionaryFilename, corpusFilename):
	# create dict, corpus
	print "Generating dictionary..."
	dictionary = corpora.Dictionary(documents)
	print "Generating corpus..."
	corpus = [dictionary.doc2bow(document) for document in documents]

	# save for later use
	remove(dictionaryFilename)
	remove(corpusFilename)
	remove(corpusFilename + ".index")
	dictionary.save(dictionaryFilename)
	corpora.MmCorpus.serialize(corpusFilename, corpus)

	return dictionary, corpus


if __name__ == '__main__':
	# parameters
	inputDir = "../data/extracted_comments/"
	wordlistDir = "../data/wordlists/"
	dictionaryFilename = "dictionary.dict"
	modelFilename = "model.lda"
	corpusFilename = "corpus.mm"
	numTopics = 5
	numPasses = 20
	reloadVSM = False
	reloadModel = True #False
	useTfidf = True
	useWordlist = False

	# extract comments if necessary
	if isfile(dictionaryFilename) and isfile(corpusFilename) and not reloadVSM:
		print "Loading dictionary and corpus from file..."
		dictionary = corpora.Dictionary.load(dictionaryFilename)
		corpus = corpora.MmCorpus(corpusFilename)
	else:
		print "No files located. Creating dictionary and corpus..."
		wordlist = set()
		if useWordlist:
			wordlist = getWordlist(getFilesOf(wordlistDir))
		documents = tokenize(extractComments(getFilesOf(inputDir)), wordlist)
		dictionary, corpus = createVSM(documents, dictionaryFilename, corpusFilename)
		reloadModel = True

	# generate model using tfidf
	if reloadModel or not isfile(modelFilename):
		print "Generating LDA model with", numPasses, "iterations..."
		if useTfidf:
			tfidf = models.TfidfModel(corpus, normalize=True)
			tfidf_corpus = tfidf[corpus]
			lda = models.ldamodel.LdaModel(corpus=tfidf_corpus, id2word=dictionary,
				num_topics=numTopics, passes=numPasses)
		else:
			lda = models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary,
				num_topics=numTopics, passes=numPasses)
		lda.save(modelFilename)
	else:
		print "Loading LDA model..."
		lda = models.LdaModel.load(modelFilename)
	for i in range (0,numTopics):
		print "topic", i + 1, ":", lda.print_topic(i)

