#!/usr/bin/env python

import configparser
import jira
import os
import json
import jira
from jira.exceptions import JIRAError

def get_jira_query_results(query_string):
	
	username, password, url = get_credentials()

	try:
		authed_jira = jira.JIRA(url, basic_auth=(username, password))
		issues = search_jira(query_string, 100, authed_jira)

		tickets = []
		query_set = set()
		all_links = []
		links_in_tickets = []
		epic_set = set()
		parent = None


		for issue in issues:
			links = issue.fields.issuelinks
			subtasks = issue.fields.subtasks
			link_data = []

			for link in links:
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

						all_links.append({
						'source': issue.key,
						'target': link.inwardIssue.key,
						'type': link.type.name,
						'direction': 'inward'
						})
					elif 'outwardIssue' in vars(link).keys():
						data['direction'] = 'outward'
						data['key'] = link.outwardIssue.key
						data['summary'] = link.outwardIssue.fields.summary
						data['status'] = link.outwardIssue.fields.status.name
						data['issuetype'] = link.outwardIssue.fields.issuetype.name
						data['priority'] = link.outwardIssue.fields.priority.name

						all_links.append({
						'source': issue.key,
						'target': link.outwardIssue.key,
						'type': link.type.name,
						'direction': 'outward'
						})
					#add data to array to be held within issue data	
					link_data.append(data)

			if 'parent' in vars(issue.fields).keys():
				parent = issue.fields.parent
				data = {
					'type': 'parent',
					'key': parent.key,
					'summary': parent.fields.summary,
					'status': parent.fields.status.name,
					'priority': parent.fields.priority.name
				}
				link_data.append(data)
				all_links.append({
					'source': issue.key,
					'target': parent.key,
					'type': 'parent'
					})

					
			for subtask in subtasks:
				if subtask is not None:
					data = {
						'type': 'subtask',
						'key': subtask.key,
						'summary': subtask.fields.summary,
						'status': subtask.fields.status.name,
						'priority': subtask.fields.priority.name
					}
					link_data.append(data)
					all_links.append({
						'source': issue.key,
						'target': subtask.key,
						'type': 'subtask'
						})

			#customfield_10007 = epic key			
			if issue.fields.customfield_10007 is not None:
				epic_set.add(issue.fields.customfield_10007)
				data = {
					'issuetype': 'Epic',
					'key': issue.fields.customfield_10007,
				}
				link_data.append(data)
				all_links.append({
					'source': issue.key,
					'target': issue.fields.customfield_10007,
					'type': 'epic parent'
					})

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
			#customfield_10006 = sprint
			if 'customfield_10006' in vars(issue.fields).keys():
				if len(issue.fields.customfield_10006) > 0:			
					for chunk in issue.fields.customfield_10006[0].split(','):
						bite = chunk.split('=')
						if  bite[0] == 'name':
							data['sprint'] = bite[1]
							break 			

			tickets.append(data)
			query_set.add(issue.key)

		for link in all_links:
			if link['source'] in query_set and link['target'] in query_set:
				link['addedBy'] = 'query'
				links_in_tickets.append(link)

		query_list = list(query_set)
		epic_list = list(epic_set)
		epic_query_string = 'issuekey in (' + ','.join(epic_list) + ')' 

		return tickets, links_in_tickets, query_list, epic_query_string, None
	
	except JIRAError as e:
		return [], [], [], "", e

def search_jira(query, split, authed_jira): 
        big_list = []
        count = 1
        second_list = [1]
        first_list = authed_jira.search_issues(query,
            fields='assignee,summary,status,issuetype,priority,project,issuelinks,subtasks,customfield_10007,customfield_10006,parent',
            startAt=0,
            maxResults=split)
        big_list.extend(first_list)
        while (len(second_list) != 0):
            second_list = authed_jira.search_issues(query,
            	fields='assignee,summary,status,issuetype,priority,project,issuelinks,subtasks,customfield_10007,customfield_10006,parent',
                startAt=(count * split),
                maxResults=((count + 1) * split))
            big_list.extend(second_list)
            count = count + 1
        return big_list 

def get_credentials():
	SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

	Config = configparser.ConfigParser()
	Config.read(SCRIPT_DIR + '/' + 'config.ini')

	return Config.get('Auth', 'username'), Config.get('Auth', 'password'), Config.get('Basic', 'url')

# def get_epic_query_results(epic_query_string):
# 	username, password, url = get_credentials()

# 	try:
# 		authed_jira = jira.JIRA(url, basic_auth=(username, password))
# 		issues = search_jira(epic_query_string, 100, authed_jira)


