import re

FILE_LOCATION = "../data/wordlists/realliwc.txt"

def parseRealLIWC():
	f = open(FILE_LOCATION, "r")
	result = {}
	for line in f.readlines():
		# identify the key
		key = line.split(":")[0]

		# parse the words
		line = line.split(":")[1]
		line = re.sub(r"\*", ".*", line)
		result[key] = re.findall("[^\s]+", line)[1:]
	f.close()
	return result

if __name__ == '__main__':
	print parseRealLIWC()