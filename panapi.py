#!/usr/bin/env python3

import re
import os 
import sys

#***************************************
#		CONFIG IMPORT
#***************************************
import config

#***************************************
#		GLOBAL VARIABLES
#***************************************

hostKeyFile = config.hostKeyFile

def collectSessions():

	hosts = collectHosts()
	for host in hosts:
		output = panApiCall(host['hostname'],host['key'])

def panApiCall(host='', key=''):

	cmd = 'panxapi.py -h {}  -Xjo \'show session all\' -K {} --text'.format(host,key)
	try:
		output = os.popen(cmd).read()
	except OSError:
		print("Error in executing command")
		sys.exit()

	return output

def collectHosts():

	with open(hostKeyFile) as f:
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

	#panApiCall()
	collectSessions()


if __name__ == "__main__":
	main()
