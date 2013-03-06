#!/usr/bin/python
# coding: utf-8

import sys, os, nltk, itertools, string, re
import strlib, codecs
import numpy as np


def extractPoem(folder):
  dict = {}
  for i in sorted(os.listdir(folder)):
    f = open(folder + '/' + i, 'r')
    #f = codecs.open(folder + '/' + i, 'r', encoding='utf-8')
    f.readline()
    lines = f.readlines()
    f.close()
    
    for l in lines:
      l = l[:-1].lower()
      l = unicode(l, 'ascii', 'ignore').encode('utf-8')
      l = re.sub(r'[\W_]+', ' ', l)
      tokens = l.split()
      for t in tokens:
        #t = unicode(t, 'ascii', 'ignore').encode('utf-8')
        if t in dict:
          dict[t] += 1
        else:
          dict[t] = 1
  return dict
  
