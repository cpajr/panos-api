#!/usr/bin/env python3

import re

#***************************************
#		CONFIG IMPORT
#***************************************
#import user

def panApiCall():

	#Collect hostnames and API keys
	print ("")

def collectHosts():

	with open('user.config') as f:
		output = f.readlines()

	returnList = []

	for line in output:
		try:
			hostname = re.search(r'^(.*):(.*)$', line).group(1)
		except AttributeError:
			hostname = ""

		try:
			key = re.search(r'^(.*):(.*)$', line).group(2)
		except AttributeError:
			key = ""

		if (hostname == ""):
			continue
		else:
			returnList.append({'hostname': hostname, 'key': key})

	return returnList

'''
*****************************************
		Main Method
*****************************************
'''
def main():

	print (collectHosts())


if __name__ == "__main__":
	main()
