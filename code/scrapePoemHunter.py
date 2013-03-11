import sys, os, re, urllib2
import HTMLParser
#from mechanize import Browser
from BeautifulSoup import BeautifulSoup
from bs4 import UnicodeDammit

def getAllHtmlFileNames(subfolder):
  filenames = []
  for files in os.walk('./' + subfolder):
      for f in files:
          filenames.append(f)
  files = []
  for f in filenames[2]:
      if os.path.splitext(f)[1] == '.html':
          files.append(f)
  return files

# Scrape Top 500 poet pages
def scrapePoetList(numPage):
  for i in range(numPage):
    url = 'http://www.poemhunter.com/p/t/l.asp?a=0&l=Top500&p=' + str(i + 1)
    page = urllib2.urlopen(url)
    f = open('../data/top500PoetList/poetList' + str(i+1) + '.html', 'w')
    f.write(page.read())
    f.close()

def crawlPoemPages(page):
  print 'Poet page ' + str(page)
  mainUrl = 'http://www.poemhunter.com/'
  f = open('../data/top500PoetList/poetList' + str(page) + '.html', 'r')
  soup = BeautifulSoup(f.read())
  f.close()
  table = soup.findAll('a', {'class':'name'})
  assert(len(table) == 50)
#   for j in range(14):
#     t = table[j]
  for t in table:
    print t['title']
    name = re.sub(r'/', '', t['href'].encode('utf-8'))
    url = mainUrl + name + '/poems/'
    soup = BeautifulSoup(urllib2.urlopen(url).read())
    table2 = soup.findAll('div', {'class': 'pagination mb-15'})
    if len(table2) != 1:
      print str(len(table2))
#     assert(len(table2) == 1)
    scrapeIndivPoemPage(mainUrl, url) # scrape this page
    if len(table2) > 0:
      maxPage = int(table2[0].findAll('a')[-1].contents[0])
  #     table3 = BeautifulSoup(table2[0].prettify()).findAll('a')
      for pageNumber in range(2, maxPage+1):
        fullUrl = url + 'page-' + str(pageNumber) + '/?a=a&amp;l=1&amp;y='
        print '\t page: ' + fullUrl
        scrapeIndivPoemPage(mainUrl, fullUrl)
              
def scrapeIndivPoemPage(mainUrl, fullUrl):
  page = urllib2.urlopen(fullUrl)
  soup = BeautifulSoup(page.read())
  table = soup.findAll('table', {'class':'poems'})
  assert(len(table) == 1)
  soup = BeautifulSoup(table[0].prettify())
  table2 = soup.findAll('a')
  for t in table2:
    subUrl = t['href'].encode('utf-8')
    page2 = urllib2.urlopen(mainUrl + subUrl)
    name = re.sub('/', ' ', subUrl).strip().split()[-1]
    assert (name.strip() is not '')
    #name = re.sub(r'\W+', '', name).encode('utf-8')
    f = open('../data/rawhtml/' + name + '.html', 'w')
    f.write(page2.read())
    f.close()
  

def cleanFile(rawFile, cleanFile):
  h = HTMLParser.HTMLParser()
  fIn = open(rawFile, 'r')
  lines = fIn.readlines()
  fIn.close()  
  fOut = open(cleanFile, 'w')
  for l in lines:
    if not l.isspace():
      dammit = UnicodeDammit(l.strip())
      print >> fOut, h.unescape(dammit.unicode_markup).encode('utf-8')
  fOut.close()
    
def main(numPage):
#   scrapePoetList(numPage)
#   for i in range(10):
#     crawlPoemPages(i+1)
  crawlPoemPages(2)

main(10)
