#!/usr/bin/env python

from jira.exceptions import JIRAError
import logging
from jira_graph_viz.jira_client import search_jira_threaded
from jira_graph_viz.issue_parser import parse_data_from_jira_api_response
from flask import flash, request
from jira_graph_viz_config import Configs
import urllib


def submit_query_with_link_levels(query, link_levels):
	merged_dataset = []
	merged_links = []
	merged_query_set = set()

	for link_level in range(link_levels):
		dataset, links, query_set, tickets_next_level = submit_query(query, link_level)
		for ticket in dataset:
			if ticket['key'] not in merged_query_set:
				merged_dataset.append(ticket)
				merged_query_set.add(ticket['key'])
		merged_links.extend(links)
		merged_query_set = merged_query_set.union(query_set)

		query = 'issuekey in ({})'.format(','.join(tickets_next_level))
	merged_query_list = list(merged_query_set)
	return merged_dataset, merged_links, merged_query_list


def submit_query(query, link_level):
	jira_configs = Configs()
	jira_connection = jira_configs.get_jira()

	flash('Query submitted: {}'.format(query))
	dataset, links, query_set, tickets_next_level, error = get_jira_query_results(
		query_string=query, jira_connection=jira_connection, link_level=link_level)

	if error is not None:
		flash('Error Code: {} - {}'.format(error.status_code, error.text))
	else:
		flash('Issues in query results: {}'.format(len(dataset)))
		url = request.url_root + "index?query=" + urllib.parse.quote(str(query))
		flash('Share this jira-graph-viz: {}'.format(url))

	return dataset, links, query_set, tickets_next_level


def get_jira_query_results(query_string, jira_connection, link_level):

	logging.basicConfig(level=logging.ERROR, format='[%(levelname)s] (%(threadName)-10s) %(message)s')

	try:
		issues = search_jira_threaded(query_string, jira_connection)
		return parse_data_from_jira_api_response(issues, link_level)
	except JIRAError as e:
		return [], [], [], [], e

