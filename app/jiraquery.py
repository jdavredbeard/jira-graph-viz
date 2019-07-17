#!/usr/bin/env python

import os
from jira.exceptions import JIRAError
import threading
import logging
import math


def get_jira_query_results(query_string, threading, jira_connection):

	logging.basicConfig(level=logging.DEBUG,
                    format='[%(levelname)s] (%(threadName)-10s) %(message)s')
	try:
		issues = search_jira_threaded(query_string, jira_connection) if threading else search_jira(query_string, 100, jira_connection)
		return parse_data_from_jira_api_response(issues)
	except JIRAError as e:
		return [], [], [], e

def parse_data_from_jira_api_response(issues):
	tickets, links_in_tickets, query_list = parse_issues(issues)
	return tickets, links_in_tickets, query_list, None

def parse_issues(issues):
	query_epic_set = set()
	query_set = set()
	tickets = []
	all_links = []

	for issue in issues:
		parsedIssue = create_parsed_issue(issue)


		links = issue.fields.issuelinks
		subtasks = issue.fields.subtasks
		link_data = []

		add_issue_links_to_link_data(issue, links, link_data, all_links)
		add_parent_to_link_data(issue, link_data, all_links)
		add_subtasks_to_link_data(issue, subtasks, link_data, all_links)

		parsedIssue = add_links_to_parsed_issue(parsedIssue, link_data)

		tickets.append(parsedIssue)

		if issue.fields.issuetype.name == 'Epic':
			query_epic_set.add(issue.key)

		query_set.add(issue.key)

	links_in_tickets = add_links_in_query_set_to_links_in_tickets(all_links, query_set)
	query_list = list(query_set)
	return tickets, links_in_tickets, query_list

def create_parsed_issue(issue):
	return parse_fields_from_issue(issue,
								fields = [{"sourceName": ("key",), "targetName": "key"},
										 {"sourceName": ("raw", "fields", "summary"), "targetName": "summary"},
										 {"sourceName": ("raw", "fields", "status","name"), "targetName": "status"},
										 {"sourceName": ("raw", "fields", "issuetype", "name"), "targetName": "issuetype"},
										 {"sourceName": ("raw","fields", "priority", "name"), "targetName": "priority"},
										 {"sourceName": ("raw", "fields", "assignee", "name"), "targetName": "assignee"}])

def create_parsed_inward_issue(issue):
	return parse_fields_from_issue(issue,
								fields = [{"sourceName": ("raw", "inwardIssue", "key"), "targetName": "key"},
										  {"sourceName": ("raw", "inwardIssue", "fields", "summary"), "targetName": "summary"},
										  {"sourceName": ("raw", "inwardIssue", "fields", "status","name"), "targetName": "status"},
										  {"sourceName": ("raw", "inwardIssue", "fields", "issuetype", "name"), "targetName": "issuetype"},
										  {"sourceName": ("raw", "inwardIssue", "fields", "priority", "name"), "targetName": "priority"},
										  {"sourceName": ("raw", "inwardIssue", "fields", "assignee", "name"), "targetName": "assignee"},
										  {"sourceName": ("raw", "type", "name"), "targetName": "type"}])

def create_parsed_outward_issue(issue):
	return parse_fields_from_issue(issue,
								fields = [{"sourceName": ("raw", "outwardIssue", "key"), "targetName": "key"},
										  {"sourceName": ("raw", "outwardIssue", "fields", "summary"), "targetName": "summary"},
										  {"sourceName": ("raw", "outwardIssue", "fields", "status","name"), "targetName": "status"},
										  {"sourceName": ("raw", "outwardIssue", "fields", "issuetype", "name"), "targetName": "issuetype"},
										  {"sourceName": ("raw", "outwardIssue", "fields", "priority", "name"), "targetName": "priority"},
										  {"sourceName": ("raw", "outwardIssue", "fields", "assignee", "name"), "targetName": "assignee"},
										  {"sourceName": ("raw", "type", "name"), "targetName": "type"}])

def parse_fields_from_issue(sourceIssue, fields):
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

def add_links_to_parsed_issue(parsedIssue, link_data):
	parsedIssue['issuelinks'] = link_data
	return parsedIssue

def add_links_in_query_set_to_links_in_tickets(all_links, query_set):
	links_in_tickets = []
	for link in all_links:
		if link['source'] in query_set and link['target'] in query_set:
			link['addedBy'] = 'query'
			links_in_tickets.append(link)
	return links_in_tickets

def add_subtasks_to_link_data(issue, subtasks, link_data, all_links):
	for subtask in subtasks:
		if subtask is not None:
			parsedSubtask = create_parsed_issue(subtask)

			parsedSubtask['type'] = 'subtask'
			link_data.append(parsedSubtask)

			all_links.append({
				'source': issue.key,
				'target': subtask.key,
				'type': 'subtask'
				})

def add_parent_to_link_data(issue, link_data, all_links):
	if 'parent' in vars(issue.fields):
		parent = issue.fields.parent
		parsedParent = create_parsed_issue(parent)

		parsedParent['type'] = 'parent'

		link_data.append(parsedParent)

		all_links.append({
			'source': issue.key,
			'target': parent.key,
			'type': 'parent'
			})

def add_issue_links_to_link_data(issue, links, link_data, all_links):
	for link in links:
		if link is not None:
			if 'inwardIssue' in vars(link):

				parsedIssue = create_parsed_inward_issue(link)
				parsedIssue['direction'] = 'inward'

				all_links.append({
				'source': issue.key,
				'target': link.inwardIssue.key,
				'type': link.type.name,
				'direction': 'inward'
				})
			elif 'outwardIssue' in vars(link):
				parsedIssue = create_parsed_outward_issue(link)

				parsedIssue['direction'] = 'outward'

				all_links.append({
				'source': issue.key,
				'target': link.outwardIssue.key,
				'type': link.type.name,
				'direction': 'outward'
				})

			link_data.append(parsedIssue)

def search_jira(query, split, jira_connection): 
    big_list = []
    count = 1
    second_list = [1]
    first_list = jira_connection.search_issues(query,
        fields='assignee,summary,status,issuetype,priority,project,issuelinks,subtasks,customfield_10007,customfield_10006,parent',
        startAt=0,
        maxResults=split)
    big_list.extend(first_list)
    while (len(second_list) != 0):
        second_list = jira_connection.search_issues(query,
        	fields='assignee,summary,status,issuetype,priority,project,issuelinks,subtasks,customfield_10007,customfield_10006,parent',
            startAt=(count * split),
            maxResults=((count + 1) * split))
        big_list.extend(second_list)
        count = count + 1
    return big_list

def search_jira_threaded(query, jira_connection):
	full_query_results = []
	threads = []
	max_query_threads = int(os.environ.get('MAX_QUERY_THREADS', 8))

	num_threads_needed = calculate_num_threads_from_total_results(query, jira_connection)

	max_threads = min(num_threads_needed, max_query_threads)

	logging.debug('max_threads = {}'.format(max_threads))

	gunicorn_threads = int(os.environ.get('GUNICORN_THREADS', 5))

	num_started_threads = 0

	while num_started_threads <= num_threads_needed:
		while threading.active_count() <= max_threads + gunicorn_threads:
			logging.debug('threading.active_count() = {}'.format(threading.active_count()))
			start_at = 100 * num_started_threads
			max_results = 100 * (num_started_threads + 1)
			t = threading.Thread(target=threaded_search_job, args=(query, jira_connection, start_at, max_results, full_query_results))
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

def calculate_num_threads_from_total_results(query, jira_connection):
	total_check_query = jira_connection.search_issues(query, fields='total')
	total_results = total_check_query.total
	num_threads_needed = math.ceil(total_results / 100)

	logging.debug('total = {}'.format(total_results))
	logging.debug('num_threads_needed = {}'.format(num_threads_needed))
	return num_threads_needed

def threaded_search_job(query, jira_connection, start_at, max_results, full_query_results):
	logging.debug('Starting')
	threaded_search_job_query_results = jira_connection.search_issues(query,
            	fields='assignee,summary,status,issuetype,priority,project,issuelinks,subtasks,customfield_10007,customfield_10006,parent',
                startAt=start_at,
                maxResults=max_results)
	full_query_results.extend(threaded_search_job_query_results)
	logging.debug('Done')
