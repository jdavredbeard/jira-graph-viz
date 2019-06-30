#!/usr/bin/env python

import os
from jira.exceptions import JIRAError
import threading
import logging
import math


def get_jira_query_results(query_string, threading, authed_jira):

	logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s',
                    )
	try:
		issues = search_jira_threaded(query_string, authed_jira) if threading else search_jira(query_string, 100, authed_jira)
		return parseDataFromJiraApiResponse(issues)
	except JIRAError as e:
		return [], [], [], "", None, e

def parseDataFromJiraApiResponse(issues):
	tickets, links_in_tickets, query_list, linked_epic_query_string, query_epic_set = parseIssues(issues)	
	return tickets, links_in_tickets, query_list, linked_epic_query_string, query_epic_set, None

def parseIssues(issues):
	linked_epic_set = set()
	query_epic_set = set()
	query_set = set()
	tickets = []
	all_links = []

	for issue in issues:
		parsedIssue = createParsedIssue(issue)

		parsedIssue = addSprintToParsedIssue(issue, parsedIssue)

		links = issue.fields.issuelinks
		subtasks = issue.fields.subtasks
		link_data = []

		addIssueLinksToLinkData(issue, links, link_data, all_links)
		addParentToLinkData(issue, link_data, all_links)
		addSubtasksToLinkData(issue, subtasks, link_data, all_links)			
		addEpicToLinkData(issue, linked_epic_set, link_data, all_links)

		parsedIssue = addLinksToParsedIssue(parsedIssue, link_data)

		tickets.append(parsedIssue)

		if issue.fields.issuetype.name == 'Epic':
			query_epic_set.add(issue.key)

		query_set.add(issue.key)

	links_in_tickets = addLinksInQuerySetToLinksInTickets(all_links, query_set)
	query_list = list(query_set)
	linked_epic_query_string = createLinkedEpicQueryString(linked_epic_set)
	return tickets, links_in_tickets, query_list, linked_epic_query_string, query_epic_set

def createParsedIssue(issue):
	return parseFieldsFromIssue(issue,
								fields = [{"sourceName": ("key",), "targetName": "key"},
										 {"sourceName": ("raw", "fields", "summary"), "targetName": "summary"},
										 {"sourceName": ("raw", "fields", "status","name"), "targetName": "status"},
										 {"sourceName": ("raw", "fields", "issuetype", "name"), "targetName": "issuetype"},
										 {"sourceName": ("raw","fields", "priority", "name"), "targetName": "priority"},
										 {"sourceName": ("raw", "fields", "assignee", "name"), "targetName": "assignee"}])

def createParsedInwardIssue(issue):
	return parseFieldsFromIssue(issue,
								fields = [{"sourceName": ("raw", "inwardIssue", "key"), "targetName": "key"},
										  {"sourceName": ("raw", "inwardIssue", "fields", "summary"), "targetName": "summary"},
										  {"sourceName": ("raw", "inwardIssue", "fields", "status","name"), "targetName": "status"},
										  {"sourceName": ("raw", "inwardIssue", "fields", "issuetype", "name"), "targetName": "issuetype"},
										  {"sourceName": ("raw", "inwardIssue", "fields", "priority", "name"), "targetName": "priority"},
										  {"sourceName": ("raw", "inwardIssue", "fields", "assignee", "name"), "targetName": "assignee"},
										  {"sourceName": ("raw", "type", "name"), "targetName": "type"}])

def createParsedOutwardIssue(issue):
	return parseFieldsFromIssue(issue,
								fields = [{"sourceName": ("raw", "outwardIssue", "key"), "targetName": "key"},
										  {"sourceName": ("raw", "outwardIssue", "fields", "summary"), "targetName": "summary"},
										  {"sourceName": ("raw", "outwardIssue", "fields", "status","name"), "targetName": "status"},
										  {"sourceName": ("raw", "outwardIssue", "fields", "issuetype", "name"), "targetName": "issuetype"},
										  {"sourceName": ("raw", "outwardIssue", "fields", "priority", "name"), "targetName": "priority"},
										  {"sourceName": ("raw", "outwardIssue", "fields", "assignee", "name"), "targetName": "assignee"},
										  {"sourceName": ("raw", "type", "name"), "targetName": "type"}])

def parseFieldsFromIssue(sourceIssue, fields):
	parsedIssue = {}
	for field in fields:
		fieldValue = get_nested(vars(sourceIssue), *field["sourceName"])
		if fieldValue is not None:
			parsedIssue[field["targetName"]] = fieldValue
	return parsedIssue

def get_nested(data, *args):
	if args and data:
		element = args[0]
		if element:
			value = data.get(element)
			return value if len(args) == 1 else get_nested(value, *args[1:])

def addSprintToParsedIssue(issue, parsedIssue):
	#customfield_10006 = sprint
	if "customfield_10006" in vars(issue.fields) and issue.fields.customfield_10006 is not None:
		if len(issue.fields.customfield_10006) > 0:
			for chunk in issue.fields.customfield_10006[0].split(','):
				bite = chunk.split('=')
				if bite[0] == 'name':
					parsedIssue['sprint'] = bite[1]
					break
	return parsedIssue

def addLinksToParsedIssue(parsedIssue, link_data):
	parsedIssue['issuelinks'] = link_data
	return parsedIssue

def createLinkedEpicQueryString(linked_epic_set):
	linked_epic_list = list(linked_epic_set)
	return 'issuekey in (' + ','.join(linked_epic_list) + ')'

def addLinksInQuerySetToLinksInTickets(all_links, query_set):
	links_in_tickets = []
	for link in all_links:
		if link['source'] in query_set and link['target'] in query_set:
			link['addedBy'] = 'query'
			links_in_tickets.append(link)
	return links_in_tickets

def addEpicToLinkData(issue, linked_epic_set, link_data, all_links):
	#customfield_10007 = epic key			
	if "customfield_10007" in vars(issue.fields) and issue.fields.customfield_10007 is not None:

		linked_epic_set.add(issue.fields.customfield_10007)

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

def addSubtasksToLinkData(issue, subtasks, link_data, all_links):			
	for subtask in subtasks:
		if subtask is not None:
			parsedSubtask = createParsedIssue(subtask)

			parsedSubtask['type'] = 'subtask'
			link_data.append(parsedSubtask)

			all_links.append({
				'source': issue.key,
				'target': subtask.key,
				'type': 'subtask'
				})

def addParentToLinkData(issue, link_data, all_links):
	if 'parent' in vars(issue.fields):
		parent = issue.fields.parent
		parsedParent = createParsedIssue(parent)

		parsedParent['type'] = 'parent'

		link_data.append(parsedParent)

		all_links.append({
			'source': issue.key,
			'target': parent.key,
			'type': 'parent'
			})

def addIssueLinksToLinkData(issue, links, link_data, all_links):
	for link in links:
		if link is not None:

			# data = {
			# 	'type': link.type.name,
			# 	# 'inwardtype': link.type.inward,
			# 	# 'outwardtype': link.type.outward,
			# }
			if 'inwardIssue' in vars(link):


				parsedIssue = createParsedInwardIssue(link)
				parsedIssue['direction'] = 'inward'


				# data['key'] = link.inwardIssue.key
				# data['summary'] = link.inwardIssue.fields.summary
				# data['status'] = link.inwardIssue.fields.status.name
				# data['issuetype'] = link.inwardIssue.fields.issuetype.name
				# if "priority" in vars(link.inwardIssue.fields) and link.inwardIssue.fields.priority is not None:
				# 	data['priority'] = link.inwardIssue.fields.priority.name

				all_links.append({
				'source': issue.key,
				'target': link.inwardIssue.key,
				'type': link.type.name,
				'direction': 'inward'
				})
			elif 'outwardIssue' in vars(link):
				parsedIssue = createParsedOutwardIssue(link)

				parsedIssue['direction'] = 'outward'

				# data['key'] = link.outwardIssue.key
				# data['summary'] = link.outwardIssue.fields.summary
				# data['status'] = link.outwardIssue.fields.status.name
				# data['issuetype'] = link.outwardIssue.fields.issuetype.name
				# if "priority" in vars(link.outwardIssue.fields) and link.outwardIssue.fields.priority is not None:
				# 	data['priority'] = link.outwardIssue.fields.priority.name

				all_links.append({
				'source': issue.key,
				'target': link.outwardIssue.key,
				'type': link.type.name,
				'direction': 'outward'
				})
			#add data to array to be held within issue data	
			link_data.append(parsedIssue)

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

def search_jira_threaded(query, authed_jira):
	full_query_results = []
	threads = []
	max_query_threads = int(os.environ.get('MAX_QUERY_THREADS', 8))

	num_threads_needed = calculate_num_threads_from_total_results(query, authed_jira)

	max_threads = min(num_threads_needed, max_query_threads)

	logging.debug('max_threads = {}'.format(max_threads))

	gunicorn_threads = int(os.environ.get('GUNICORN_THREADS', 5))

	num_started_threads = 0

	while num_started_threads <= num_threads_needed:
		while threading.active_count() <= max_threads + gunicorn_threads:
			logging.debug('threading.active_count() = {}'.format(threading.active_count()))
			start_at = 100 * num_started_threads
			max_results = 100 * (num_started_threads + 1)
			t = threading.Thread(target=threaded_search_job, args=(query, authed_jira, start_at, max_results, full_query_results))
			threads.append(t)
			t.start()
			num_started_threads += 1
		
	for thread in threads:
		if thread.is_alive():
			logging.debug('{} still alive'.format(thread.getName()))
			thread.join()
			logging.debug('{} joined {}'.format(thread.getName(), threading.currentThread().getName()))
	logging.debug('Returning full_query_results')
	return full_query_results

def calculate_num_threads_from_total_results(query, authed_jira):
	total_check_query = authed_jira.search_issues(query, fields='total')
	total_results = total_check_query.total
	num_threads_needed = math.ceil(total_results / 100)

	logging.debug('total = {}'.format(total_results))
	logging.debug('num_threads_needed = {}'.format(num_threads_needed))
	return num_threads_needed

def threaded_search_job(query, authed_jira, start_at, max_results, full_query_results):
	logging.debug('Starting')
	threaded_search_job_query_results = authed_jira.search_issues(query,
            	fields='assignee,summary,status,issuetype,priority,project,issuelinks,subtasks,customfield_10007,customfield_10006,parent',
                startAt=start_at,
                maxResults=max_results)
	full_query_results.extend(threaded_search_job_query_results)
	logging.debug('Done')
