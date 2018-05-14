#!/usr/bin/env python

import configparser
import jira
import os
import json

SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

Config = configparser.ConfigParser()
Config.read(SCRIPT_DIR + '/' + 'config.ini')

url = Config.get('Basic', 'url')
username = Config.get('Auth', 'username')
password = Config.get('Auth', 'password')


authed_jira = jira.JIRA(url, basic_auth=(username, password))
issues = authed_jira.search_issues('project=EAQ and sprint = "EAQ Sprint 15" and issuetype != Sub-task')

tickets = []
links = []


for issue in issues:
	jira_links = issue.fields.issuelinks
	link_data = []

	for link in jira_links:
		if link is not None:

			data = {
				'type': link.type.name,
				'inwardtype': link.type.inward,
				'outwardtype': link.type.outward,
			}
			if 'inwardIssue' in vars(link).keys():
				data['direction'] = 'inward'
				data['key'] = link.inwardIssue.key
				data['summary'] = link.inwardIssue.fields.summary
				data['status'] = link.inwardIssue.fields.status.name
				data['issuetype'] = link.inwardIssue.fields.issuetype.name
				data['priority'] = link.inwardIssue.fields.priority.name

				#d3 links array
				links.append({
				'source': issue.key,
				'target': link.inwardIssue.key,
				'strength': 0.7
				})
			elif 'outwardIssue' in vars(link).keys():
				data['direction'] = 'outward'
				data['key'] = link.outwardIssue.key
				data['summary'] = link.outwardIssue.fields.summary
				data['status'] = link.outwardIssue.fields.status.name
				data['issuetype'] = link.outwardIssue.fields.issuetype.name
				data['priority'] = link.outwardIssue.fields.priority.name

				links.append({
				'source': link.outwardIssue.key,
				'target': issue.key,
				'strength': 0.7
				})
			#add data to array to be held within issue data	
			link_data.append(data)
			#also add linked issue as its own issue (for d3 nodes)
			tickets.append(data)

	data = {
		'key': issue.key,
		'summary': issue.fields.summary,
		'status': issue.fields.status.name,
		'issuetype': issue.fields.issuetype.name,
		'priority': issue.fields.priority.name,
		'project': issue.fields.project.name,
		'issuelinks': link_data
	}
	if issue.fields.assignee is not None:
		data['assignee'] = issue.fields.assignee.name
	if issue.fields.customfield_10006[0] is not None:
		for chunk in issue.fields.customfield_10006[0].split(','):
			bite = chunk.split('=')
			if  bite[0] == 'name':
				data['sprint'] = bite[1]
				break 

	tickets.append(data)

print(json.dumps(tickets, sort_keys=True, indent=2, separators=(',', ': ')))
print(json.dumps(links, sort_keys=True, indent=2, separators=(',', ': ')))



