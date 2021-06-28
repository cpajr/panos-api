#!/usr/bin/env python3

import re
import os 
import sys
import json
from datetime import datetime
import pprint	
import math

#***************************************
#		CONFIG IMPORT
#***************************************
import config

#***************************************
#		CLASSES
#***************************************

class Session():

	def __init__(self):
		self.list_entries = []

	def add(self, session):

		if (len(self.list_entries) == 0):
			
			self.list_entries.append(
				{'src': session['src'],
				'session_count':1,
				'session-list':[session]})
		else:
			d = next((item for item in self.list_entries if item['src'] == session['src']), False)
			if (d):
				d['session_count'] += 1
				#tmpStr = 'session' + str(d['session_count'])
				#d[tmpStr] = session
				d['session-list'].append(session)

			else:
				self.list_entries.append(
						{'src': session['src'],
						'session_count':1,
						'session-list':[session]}
					)
	def print(self):
		print ("****************Begin List****************")
		for entry in self.list_entries:
			#if (entry['session_count'] > 1):
			print (entry)
				#pprint.pprint(entry)
			print("")
		print ("****************End List******************")

#***************************************
#		GLOBAL VARIABLES
#***************************************

hostKeyFile = config.hostKeyFile
sessObj = Session()

def collectSessions():

	hosts = collectHosts()
	for host in hosts:
		panApiCall(host['hostname'],host['key'])
		#output = json.loads(panApiCall(host['hostname'],host['key']))

		#processSessions(output['response']['result']['entry'])

def processSessions(data):

	count = 0

	for item in data:

		# duration = procTimestamp(item['start-time'])

		# if (item['source'] == "10.101.2.41"):
		# 	print ("{}->{}, {}".format(item['source'],item['dst'],item['application']))

		# tmp = {'src': item['source'],'dst':item['dst'], 'app': item['application'], 'amt_data': int(item['total-byte-count']), 'session_length': duration }

		# if (tmp['session_length'] > 172800):
		#  	sessObj.add(tmp)
		count += 1


def procTimestamp(strStamp=''):

	timestamp = datetime.strptime(strStamp,"%a %b %d %H:%M:%S %Y")
	current_timestamp = datetime.now()
	td = current_timestamp - timestamp

	return int(td.total_seconds())

def panApiCall(host='', key=''):

	'''
	We need to get the total count of sessions so that we can
	properly form the requests to get the full list.  PANOS limits 
	return list to 1024 entries.  
	'''
	countXmlCmd = 'type=op&cmd=<show><session><all><filter><count>yes</count></filter></all></session></show>&key={}'.format(key)
	countCmd = 'panxapi.py -h {}  -Xj -K {} --text --ad-hoc \'{}\''.format(host,key,countXmlCmd)
	try:
		countOutput = os.popen(countCmd).read()
	except OSError:
		print("Error in executing command")
		sys.exit()

	countOutputJson = json.loads(countOutput)
	count = int(countOutputJson['response']['result']['member'][0])
	print (count)
	'''
	With the count of sessions in hand, we will not iterate through 
	and get the entire list of sessions
	'''
	tmpNum = count // 1024.0
	print (tmpNum)
	numIterate = math.ceil(tmpNum)
	print (numIterate)
	tmp = 'type=op&cmd=<show><session><all><start-at>1024</start-at></all></session></show>&key={}'.format(key)

	#cmd = 'panxapi.py -h {}  -Xjo \'show session all start-at 6400\' -K {} --text'.format(host,key)
	cmd = 'panxapi.py -h {}  -Xj -K {} --text --ad-hoc \'{}\''.format(host,key,tmp)

	try:
		output = os.popen(cmd).read()
	except OSError:
		print("Error in executing command")
		sys.exit()

	returnOutput = json.loads(output)
	#print (returnOutput['response']['result']['entry'])
	#print (output)
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
	#sessObj.print()


if __name__ == "__main__":
	main()
