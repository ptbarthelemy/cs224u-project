import sys
import re
from os.path import isfile
from os import listdir
from gensim import corpora, models, similarities

STOPWORDS = ['for', 'a', 'of', 'the', 'and', 'to', 'in']

def commentFiles(dirname):
	return [dirname + f for f in listdir(dirname) if isfile(dirname + f)]

def extractComments(filenames):
	print "Reading files..."
	comments = []
	numFilesSeen = 0
	for filename in filenames:
		# numFilesSeen += 1
		# if numFilesSeen > 100:
		# 	return comments # DEBUG

		f = open(filename)
		comments.extend(re.findall(r"Commenter:[\w ]+\|\|\|  (.*)  \|\|\| likes", f.read()))
		f.close()
	return comments

def tokenize(documents):
	# remove stop words (optional?)
	print "Cleaning comments..."
	texts = [[word.lower() for word in re.findall("[A-Za-z]+", document) if word not in STOPWORDS]
		for document in documents]

	# remove words that appear only once
	print "Removing words that appear only once..."
	all_tokens = sum(texts, [])
	counts = {}
	for t in all_tokens:
		counts[t] = counts.get(t, 0) + 1
	tokens_once = set(t for t in counts.keys() if counts.get(t) == 1)
	# tokens_once = set(word for word in set(all_tokens) if all_tokens.count(word) == 1)
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
	dictionary.save(dictionaryFilename)
	corpora.MmCorpus.serialize(corpusFilename, corpus)

	return dictionary, corpus


if __name__ == '__main__':
	# parameters
	inputDir = "../data/extracted_comments/"
	dictionaryFilename = "dictionary.dict"
	modelFilename = "model.lda"
	corpusFilename = "corpus.mm"
	numTopics = 10
	reloadModel = True #False
	useTfidf = True

	# extract comments if necessary
	if isfile(dictionaryFilename) and isfile(corpusFilename):
		print "Loading dictionary and corpus from file."
		dictionary = corpora.Dictionary.load(dictionaryFilename)
		corpus = corpora.MmCorpus(corpusFilename)
	else:
		print "No files located. Creating dictionary and corpus..."
		# print "Comment files", commentFiles(inputDir)
		documents = tokenize(extractComments(commentFiles(inputDir)))
		dictionary, corpus = createVSM(documents, dictionaryFilename, corpusFilename)
		reloadModel = True
	print "Loaded",dictionary, corpus

	# generate model using tfidf
	if reloadModel or not isfile(modelFilename):
		print "Creating LDA model..."
		if useTfidf:
			tfidf = models.TfidfModel(corpus)
			corpus_tfidf = tfidf[corpus]
			lda = models.ldamodel.LdaModel(corpus=corpus_tfidf, id2word=dictionary,
				num_topics=numTopics) #, update_every=1, chunksize=1000, passes=5)
		else:
			lda = models.ldamodel.LdaModel(corpus=corpus, id2word=dictionary,
				num_topics=numTopics) #, update_every=1, chunksize=1000, passes=5)
		lda.save(modelFilename)
	else:
		print "Loading LDA model..."
		lda = models.LdaModel.load(modelFilename)
	for i in range (0,numTopics):
		print "topic", i + 1, ":", lda.print_topic(i)

