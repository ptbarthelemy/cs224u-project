import os, sys, operator

def printEmotiveWordScores(dict, outFileName):
  sorted_dict = sorted(dict.iteritems(), key = operator.itemgetter(1))
  f = open(outFileName, 'w')
  print >> f, '\n'.join(['%s\t%f' % (k,v) for (k,v) in sorted_dict])
  f.close()

f = open('../data/NRC-lexicon.txt', 'r')
nrc = f.readlines()
f.close()

f= open('../data/rtSentiScoresFull.txt', 'r')
rt = f.readlines()
f.close()

cate = {}
cate['anger'] = {}
cate['anticipation'] = {}
cate['disgust'] = {}
cate['fear'] = {}
cate['joy'] = {}
cate['negative'] = {}
cate['positive'] = {}
cate['sadness'] = {}
cate['surprise'] = {}
cate['trust'] = {}

rtScores = {}
for line in rt:
  tuple = line.strip().split('|')
  assert(len(tuple)==2)
  rtScores[tuple[0]] = float(tuple[1])
  
for line in nrc:
  tuple = line.strip().split('\t')
  if tuple[0] in rtScores and tuple[2] == '1':
    cate[tuple[1]][tuple[0]] = rtScores[tuple[0]]
#     cate[tuple[1]].add('\t'.join([tuple[0], tuple[2]]))
#     score = float(tuple[2]) 


printEmotiveWordScores(cate['anger'], '../data/anger_rt.txt')
printEmotiveWordScores(cate['anticipation'], '../data/anticipation_rt.txt')
printEmotiveWordScores(cate['disgust'], '../data/disgust_rt.txt')
printEmotiveWordScores(cate['fear'], '../data/fear_rt.txt')
printEmotiveWordScores(cate['joy'], '../data/joy_rt.txt')
printEmotiveWordScores(cate['negative'], '../data/negative_rt.txt')
printEmotiveWordScores(cate['positive'], '../data/positive_rt.txt')
printEmotiveWordScores(cate['sadness'], '../data/sadness_rt.txt')
printEmotiveWordScores(cate['surprise'], '../data/surprise_rt.txt')
printEmotiveWordScores(cate['trust'], '../data/trust_rt.txt')

