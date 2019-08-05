#!/usr/bin/env python

from jira.exceptions import JIRAError
import logging
from jira_graph_viz.jira_client import search_jira_threaded
from jira_graph_viz.issue_parser import parse_data_from_jira_api_response
from flask import flash, request
from jira_graph_viz_config import Configs
import urllib


def submit_query(query):
	jira_configs = Configs()
	jira_connection = jira_configs.get_jira()
	jira_base_url = jira_configs.get_url()

	flash('Query submitted: {}'.format(query))
	dataset, links, query_list, linked_epic_query_string, query_epic_set, error = get_jira_query_results(
		query_string=query, jira_connection=jira_connection)

	if error is not None:
		flash('Error Code: {} - {}'.format(error.status_code, error.text))
	else:
		add_linked_epics_to_dataset_links(dataset, linked_epic_query_string,jira_connection)
		add_children_of_epics_in_query_epic_set_to_dataset(dataset, query_epic_set, jira_connection)
		flash('Issues in query results: {}'.format(len(dataset)))
		url = request.url_root + "index?query=" + urllib.parse.quote(str(query))
		flash('Share this jira-graph-viz: {}'.format(url))

	return dataset, links, query_list, jira_base_url


def get_jira_query_results(query_string, jira_connection):

	logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s')

	try:
		issues = search_jira_threaded(query_string, jira_connection)
		return parse_data_from_jira_api_response(issues)
	except JIRAError as e:
		return [], [], [], '', [], e


def add_children_of_epics_in_query_epic_set_to_dataset(dataset, query_epic_set, jira_connection):
	if len(query_epic_set) > 0:
		epic_link_hash = {}
		if len(query_epic_set) > 1:
			query_epics_for_epic_link_query = tuple(query_epic_set)
		else:
			query_epics_for_epic_link_query = '({})'.format(query_epic_set.pop())

		query_string = '"Epic Link" in {}'.format(query_epics_for_epic_link_query)

		epic_link_dataset, _, _, _, _, _ = get_jira_query_results(query_string, jira_connection)
		for issue in epic_link_dataset:
			for linked_issue in issue['issuelinks']:
				if 'issuetype' in linked_issue and linked_issue['issuetype'] == 'Epic':
					epic_key = linked_issue['key']
					if epic_key in epic_link_hash:
						epic_link_hash[epic_key].append(issue)
					else:
						epic_link_hash[epic_key] = [issue]
		for issue in dataset:
			if issue['key'] in epic_link_hash:
				for epic_link_issue in epic_link_hash[issue['key']]:
					issue['issuelinks'].append(epic_link_issue)


def add_linked_epics_to_dataset_links(dataset, linked_epic_query_string, jira_connection):
	epic_hash = {}
	if linked_epic_query_string != 'issuekey in ()':
		flash('Linked Epic query submitted: {}'.format(linked_epic_query_string))
		#get data for epics that are 'linked' to tickets in initial query and add them as links
		linked_epic_dataset, _, _, _, _, _ = get_jira_query_results(linked_epic_query_string, jira_connection)

		for epic in linked_epic_dataset:
			if 'key' in epic:
				epic_hash[epic['key']] = epic
		for issue in dataset:
			for linked_issue in issue['issuelinks']:
				if linked_issue['key'] in epic_hash and 'issuetype' in linked_issue and linked_issue[
					'issuetype'] == 'Epic':
					if 'summary' in epic_hash[linked_issue['key']]:
						linked_issue['summary'] = epic_hash[linked_issue['key']]['summary']
					if 'priority' in epic_hash[linked_issue['key']]:
						linked_issue['priority'] = epic_hash[linked_issue['key']]['priority']
					if 'status' in epic_hash[linked_issue['key']]:
						linked_issue['status'] = epic_hash[linked_issue['key']]['status']