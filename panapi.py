#!/usr/bin/env python3

import re
import os 
import sys

#***************************************
#		CONFIG IMPORT
#***************************************
#import user

def panApiCall():

	#Collect hostnames and API keys
	hosts = collectHosts()
	returnOutput = ""
	for host in hosts:

		cmd = 'panxapi.py -h {}  -Xjo \'show session all\' -K {} --text'.format(host['hostname'],host['key'])

		try:
			output = os.popen(cmd).read()
		except OSError:
			print ("Error in executing command")
			sys.exit()

		returnOutput += output 
	print (returnOutput)

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

	panApiCall()


if __name__ == "__main__":
	main()
