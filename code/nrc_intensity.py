import os, sys, operator

def printEmotiveWordScores(dict, outFileName):
  sorted_dict = sorted(dict.iteritems(), key = operator.itemgetter(1), reverse = True)
  f = open(outFileName, 'w')
  print >> f, '\n'.join(['%s\t%f' % (k,v) for (k,v) in sorted_dict])
  f.close()

def reverseScore(dict):
  for d in dict:
    dict[d] = 1-dict[d]
  return dict

def bimodalScore(dict):
  for d in dict:
    dict[d] = abs(dict[d] - 0.5) * 2
  return dict

def processNrcWords():
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
  
  cate['anger'] = reverseScore(cate['anger'])
  cate['disgust'] = reverseScore(cate['disgust'])
  cate['fear'] = reverseScore(cate['fear'])
  cate['negative'] = reverseScore(cate['negative'])
  cate['sadness'] = reverseScore(cate['sadness'])
  cate['anticipation'] = bimodalScore(cate['anticipation'])
  cate['surprise'] = bimodalScore(cate['surprise'])
  
  return cate

def printAllToFiles(cate):
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
  
def main():
  cate = processNrcWords()
  printAllToFiles(cate)