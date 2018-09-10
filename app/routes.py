from flask import render_template, flash
from flask import request
from flask import url_for
from app import app
from app.forms import QueryForm
from app.jiraquery import get_jira_query_results
from app.jiraquery import get_jira_auth
import threading
import logging
import jira


@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
def index():
	form = QueryForm()
	if form.validate_on_submit():
		flash('Query submitted: {}'.format(form.query.data))
		return submit_query(form.query.data)
	else:
		return displayHome()

@app.route('/query', methods=['GET','POST'], )
def query():

	query = request.args.get('query')
	if query:
		flash('Query submitted: {}'.format(query))
		return submit_query(query)
	else:
		return index()

@app.route('/health', methods=['GET'])
def health():
	return 'JIRA-GRAPH-VIZ Online'

def submit_query(query):

	dataset = {}
	links = {}
	query_list = []
	linked_epic_dataset = []
	epic_links = []
	epic_query_list = []
	linked_epic_query_string = ""
	epic_hash = {}
	epic_link_hash = {}
	authed_jira = get_jira_auth()

	dataset, links, query_list, linked_epic_query_string, error, query_epic_set = get_jira_query_results(
		query_string=query, threading=True, authed_jira=authed_jira)

	if error is not None:
		flash('Error Code: {} - {}'.format(error.status_code, error.text))
	else:
		if linked_epic_query_string != 'issuekey in ()':
			flash('Linked Epic query submitted: {}'.format(linked_epic_query_string))
			linked_epic_dataset, _, _, _, _, _ = get_jira_query_results(query_string=linked_epic_query_string,
																		threading=True, authed_jira=authed_jira)
			for epic in linked_epic_dataset:
				epic_hash[epic['key']] = epic
			for issue in dataset:
				for linked_issue in issue['issuelinks']:
					if linked_issue['key'] in epic_hash and 'issuetype' in linked_issue and linked_issue[
						'issuetype'] == 'Epic':
						linked_issue['summary'] = epic_hash[linked_issue['key']]['summary']
						linked_issue['priority'] = epic_hash[linked_issue['key']]['priority']
						linked_issue['status'] = epic_hash[linked_issue['key']]['status']
		if query_epic_set:
			query_epic_tuple = tuple(query_epic_set)
			epic_link_dataset, _, _, _, _, _ = get_jira_query_results(
				query_string='"Epic Link" in {}'.format(query_epic_tuple), threading=True, authed_jira=authed_jira)
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
		flash('Issues in query results: {}'.format(len(dataset)))
		url = request.url_root + "query?query=" + str(query)
		flash('Share this jira-graph-viz: {}'.format(url))

		form = QueryForm()
		form.query.data = query
	return render_template('index.html', form=form, dataset=dataset, links=links, query_list=query_list)

def displayHome():
	dataset = {}
	links = {}
	query_list = []
	return render_template('index.html', form=QueryForm(), dataset=dataset, links=links, query_list=query_list)