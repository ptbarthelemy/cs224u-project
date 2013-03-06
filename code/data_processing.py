import sys, os, nltk, itertools, string
import strlib
import numpy as np


def extractPoem(folder):
  dict = {}
  for i in sorted(os.listdir(folder)):
    f = open(folder + '/' + i, 'r')
    f.readline()
    lines = f.readlines()
    f.close()
    
    for l in lines:
      tokens = l[:-1].lower().split()
      for t in tokens:
        if t in dict:
          dict[t] += 1
        else:
          dict[t] = 1
  return dict
          
def main():
  poem_folder = '../data/extracted_poems/'
  d = extractPoem(poem_folder)

main()
