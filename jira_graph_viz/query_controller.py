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
	dataset, links, query_list, error = get_jira_query_results(
		query_string=query, jira_connection=jira_connection)

	if error is not None:
		flash('Error Code: {} - {}'.format(error.status_code, error.text))
	else:
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
		return [], [], [], e

