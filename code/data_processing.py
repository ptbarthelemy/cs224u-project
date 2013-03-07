#!/usr/bin/python
# coding: utf-8

import sys, os, nltk, itertools, string, re, codecs
import strlib, process_text, emo_count
import numpy as np

def getPosNegLists(positiveWords, negativeWords, wordsDict):
  count = 0
  pos = []
  neg = []
  for word, freq in sorted(wordsDict.items(), key=lambda (x,y): -y):
    if word not in positiveWords and word not in negativeWords:
      #print word, '\t Neutral'
      continue
    if word in positiveWords:
      pos.append((word, freq))
    else:
      assert(word in negativeWords)
      neg.append((word, freq))
    if len(pos) >= 20 and len(neg) >= 20:
      break
  return pos, neg
    
def printTop20s(pos, neg, source):
  print '\nFrom ', source
  print 'Most Freq Positive Words'
  print '\n'.join(['%s\t\t%d' % (k,v) for k,v in pos[:20]])
  print '\n'
  print 'Most Freq Negative Words'
  print '\n'.join(['%s\t\t%d' % (k,v) for k,v in neg[:20]])
  

positiveWords = set(emo_count.getWordsOf(["../data/wordlists/LoughranMcDonald_Positive.csv"]).keys())
negativeWords = set(emo_count.getWordsOf(["../data/wordlists/LoughranMcDonald_Negative.csv"]).keys())
commentsDict = emo_count.getWordsOf(emo_count.getFilesOf("../data/extracted_comments/"))

poem_folder = '../data/extracted_poems/'
poemsDict = process_text.extractPoem(poem_folder)
poemsWordList = sorted(poemsDict.keys())


(pos, neg) = getPosNegLists(positiveWords, negativeWords, commentsDict)
printTop20s(pos, neg, 'Comments')

(pos, neg) = getPosNegLists(positiveWords, negativeWords, poemsDict)
printTop20s(pos, neg, 'Poems')



