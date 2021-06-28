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
		if (session['session_length'] > 172800 and session['src-zone'] == 'Inside' and session['dst-zone'] == 'Public'):
			if (len(self.list_entries) == 0):
				
				self.list_entries.append(
					{'src': session['src'],
					'session_count':1,
					'session-list':[session]})
			else:
				d = next((item for item in self.list_entries if item['src'] == session['src']), False)
				if (d):
					d['session_count'] += 1
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
			print (entry)
			print("")
		print ("****************End List******************")

#***************************************
#		GLOBAL VARIABLES
#***************************************

hostKeyFile = config.hostKeyFile
sessObj = Session()

def collectSessions():

	'''
	This method will be called from the main routine.  It will 
	call the method to collect the list of hosts from host-key.conf.
	
	Once the list is collected, it will then pass that list to 
	panApiCall which will collect the list of sessions from the firewall.  

	With the output received, the sessions will be sent for processing.  
	'''

	hosts = collectHosts()
	for host in hosts:
		output = panApiCall(host['hostname'],host['key'])
		processSessions(output)

def processSessions(data):

	'''
	Will iterate through the list of sessions and will add 
	the session to the created class object.
	'''

	count = 0

	for item in data:

		duration = procTimestamp(item['start-time'])
		tmp = {'src': item['source'],
				'src-zone': item['from'],
				'dst':item['dst'], 
				'dst-zone': item['to'],
				'app': item['application'], 
				'amt_data': int(item['total-byte-count']), 
				'session_length': duration }

		sessObj.add(tmp)

def procTimestamp(strStamp=''):

	'''
	This will take the start time of session, as a string, 
	and converts it to a python datetime object and then 
	calculates the actual duration of the session.  
	'''

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

	'''
	With the count of sessions in hand, we will not iterate through 
	and get the entire list of sessions
	'''
	
	numIterate = math.ceil(count / 1024)

	i = 0
	returnOutput = []
	while i < numIterate:
		num = (i * 1024) + 1
		
		xmlCmd = 'type=op&cmd=<show><session><all><start-at>{}</start-at></all></session></show>&key={}'.format(num, key)
		cmd = 'panxapi.py -h {}  -Xj -K {} --text --ad-hoc \'{}\''.format(host,key,xmlCmd)
		try:
			output = os.popen(cmd).read()
		except OSError:
			print("Error in executing command")
			sys.exit()

		i += 1
		
		tmpOutput = json.loads(output)
		try:
			tmpOut = tmpOutput['response']['result']['entry']
		except TypeError:
			print ("outside")
			continue

		returnOutput.extend(tmpOut)

	return returnOutput

def collectHosts():

	with open(hostKeyFile) as f:
		output = f.readlines()
	returnList = []
	for line in output:
		if (re.search(r'^#.*',line)):
			continue
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

	collectSessions()
	sessObj.print()


if __name__ == "__main__":
	main()
