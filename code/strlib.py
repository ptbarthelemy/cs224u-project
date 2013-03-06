#!/usr/bin/python

import re

def removeNonLetters(line):
  return re.sub(r'[\s\W]+', ' ', line)
    


def removeTags(decapLine):
  decapLine = ' ' + decapLine + ' '
  decapLine = re.sub(' em ', ' ', decapLine).strip()
  decapLine = re.sub(' b ', ' ', decapLine).strip()
  return decapLine
  
def tokenize(line):
  line = re.sub('\.', ' . ', line)
  line = re.sub('\'', ' \'', line)
  line = re.sub('\"', ' \' \' ', line)
  line = re.sub(',' , ' , ', line)
  ## return re.split('\.| ', line)
  return line.split()

def formatString(line):
    line = re.sub('\.', ' . ', line)
    line = re.sub('\"', ' \'\' ', line)
    line = re.sub(',' , ' , ', line)
    line = re.sub('!' , ' ! ', line)
    line = re.sub(';' , ' ; ', line)
    line = re.sub('\(', ' ( ', line)
    line = re.sub('\)', ' ) ', line)
    line = re.sub(':', ' : ', line)
    line = re.sub('\?', ' ? ', line)
    line = re.sub('n\'t', ' n\'t', line)
    line = re.sub('\'s ', ' \'s ', line)
    line = re.sub('\'re ', ' \'re ', line)
    line = re.sub('\'d ', ' \'d ', line)
    line = re.sub('\'ve ', ' \'ve ', line)
    line = re.sub(r'\s+', ' ', line)
    line = re.sub('\. \. \.', '...', line)
    line = re.sub('\.\.\. \.', '...', line)
    return line.strip()

def stripString(line):
    line = re.sub('\.', ' . ', line)
    line = re.sub('\'', ' \'', line)
    line = re.sub('\"', ' \' \' ', line)
    line = re.sub(',' , ' , ', line)
    line = re.sub('!' , ' ! ', line)
    line = re.sub(';' , ' ; ', line)
    line = re.sub('\(', ' ( ', line)
    line = re.sub('\)', ' ) ', line)
    line = re.sub(':', ' : ', line)
    line = re.sub('\?', ' ? ', line)
    return re.sub(r'[\s\W]+', ' ', line).strip()

def decapFirstCharAfterPeriod(line, movieTitle):
    titleMatch = re.finditer(movieTitle, line)
    titlePositions = set()
    for m in titleMatch:
        titlePositions.add(m.start())
    match = re.finditer('\.(\s)*', line)
    tokens = list(line)
    for m in match:
        if len(tokens) != m.end():
            if m.end() not in titlePositions:
                tokens[m.end()] = tokens[m.end()].lower()
    if 0 not in titlePositions:
        tokens[0] = tokens[0].lower()
    return ''.join(tokens)
  
def edit_distance(misspelled_orig, correct_orig, num_edit):
  if misspelled_orig == correct_orig and num_edit >= 0:
    return True
  elif num_edit == 0:
    return False
  else:
    misspelled = ' ' + misspelled_orig + ' '
    correct = ' ' + correct_orig + ' '
    if len(misspelled) == len(correct):
      # equal length: substitution | transposition
      for i in range(len(correct)):
        if misspelled[i] != correct[i]:
          # substitution
          if misspelled[i+1: ] == correct[i+1: ]:
            return True#('sub', correct[i], misspelled[i])
          # tranposition
          elif i+1 < len(correct) and misspelled[i+1] == correct[i] and misspelled[i] == correct[i+1] and misspelled[i+2: ] == correct[i+2: ]:
            return True#('trans', correct[i], correct[i+1])
          elif num_edit == 1:
            return False
          else:
            return edit_distance(misspelled[i+1:], correct[i+1:], num_edit-1)
            #('error', '', '')
    elif len(misspelled) > len(correct):
      # insertion
      for i in range(len(correct)):
        if misspelled[i] != correct[i]:
          return edit_distance(misspelled[:i] + misspelled[i+1:], correct, num_edit-1)
          #('ins', misspelled[i-1], misspelled[i])
    else:
      # deletion: len(misspelled) < len(correct)
      for i in range(len(misspelled)):
        if misspelled[i] != correct[i]:
          return edit_distance(misspelled, correct[:i] + correct[i+1:], num_edit-1)
          #('del', correct[i-1], correct[i])
    return True#('matched', '', '')