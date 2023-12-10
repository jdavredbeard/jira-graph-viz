# Copyright 2019 Elsevier Inc.

# This file is part of jira-graph-viz.

# jira-graph-viz is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# jira-graph-viz is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with jira-graph-viz.  If not, see <https://www.gnu.org/licenses/>

#!/usr/bin/env python

from jira.exceptions import JIRAError
import logging
from jira_graph_viz.jira_client import search_jira_threaded
from jira_graph_viz.issue_parser import parse_issues
from flask import flash, request
import urllib
import jira
import os

JIRA_BASE_URL = os.environ.get('JIRA_BASE_URL', 'https://jira.atlassian.com')

def get_token_authed_jira():
    return jira.JIRA(options={'server': JIRA_BASE_URL})

def submit_query_with_link_levels(query, link_levels):
	url = request.url_root + "index?query=" + urllib.parse.quote(str(query))
	flash('Share this jira-graph-viz: {}'.format(url))
	merged_tickets = []
	merged_links = []
	merged_query_set = set()

	for link_level in range(link_levels):
		tickets, links, query_set, tickets_next_level = submit_query(query, link_level)
		for ticket in tickets:
			if ticket['key'] not in merged_query_set:
				merged_tickets.append(ticket)
				merged_query_set.add(ticket['key'])
		merged_links.extend(links)
		merged_query_set = merged_query_set.union(query_set)

		query = 'issuekey in ({})'.format(','.join(tickets_next_level))
	merged_query_list = list(merged_query_set)
	return merged_tickets, merged_links, merged_query_list


def submit_query(query, link_level):
	jira_connection = get_token_authed_jira()

	flash('Query submitted: {}'.format(query))
	tickets, links_in_tickets, query_set, tickets_next_level, error = get_jira_query_results(
		query_string=query, jira_connection=jira_connection, link_level=link_level)

	if error is not None:
		flash('Error Code: {} - {}'.format(error.status_code, error.text))

	return tickets, links_in_tickets, query_set, tickets_next_level


def get_jira_query_results(query_string, jira_connection, link_level):

	logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] (%(threadName)-10s) %(message)s')

	try:
		issues = search_jira_threaded(query_string, jira_connection)
		return parse_issues(issues, link_level)
	except JIRAError as e:
		return [], [], set(), set(), e


def add_children_of_epics_in_query_epic_set_to_tickets(tickets, query_epic_set, jira_connection):
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
		for issue in tickets:
			if issue['key'] in epic_link_hash:
				for epic_link_issue in epic_link_hash[issue['key']]:
					issue['issuelinks'].append(epic_link_issue)


def add_linked_epics_to_dataset_links(tickets, linked_epic_query_string, jira_connection):
	epic_hash = {}
	if linked_epic_query_string != 'issuekey in ()':
		flash('Linked Epic query submitted: {}'.format(linked_epic_query_string))
		#get data for epics that are 'linked' to tickets in initial query and add them as links
		linked_epic_dataset, _, _, _, _, _ = get_jira_query_results(linked_epic_query_string, jira_connection)

		for epic in linked_epic_dataset:
			if 'key' in epic:
				epic_hash[epic['key']] = epic
		for issue in tickets:
			for linked_issue in issue['issuelinks']:
				if linked_issue['key'] in epic_hash and 'issuetype' in linked_issue and linked_issue[
					'issuetype'] == 'Epic':
					if 'summary' in epic_hash[linked_issue['key']]:
						linked_issue['summary'] = epic_hash[linked_issue['key']]['summary']
					if 'priority' in epic_hash[linked_issue['key']]:
						linked_issue['priority'] = epic_hash[linked_issue['key']]['priority']
					if 'status' in epic_hash[linked_issue['key']]:
						linked_issue['status'] = epic_hash[linked_issue['key']]['status']