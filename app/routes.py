from flask import render_template, flash
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

	if form.validate_on_submit():
		flash('Query submitted: {}'.format(form.query.data))

		
		dataset, links, query_list, linked_epic_query_string, error, query_epic_set = get_jira_query_results(query_string = form.query.data, threading = True, authed_jira = authed_jira)
		
		if error is not None:
			flash('Error Code: {} - {}'.format(error.status_code, error.text))
		else:
			if linked_epic_query_string != 'issuekey in ()':    
				flash('Linked Epic query submitted: {}'.format(linked_epic_query_string))
				linked_epic_dataset, _, _, _, _, _ = get_jira_query_results(query_string = linked_epic_query_string, threading= False, authed_jira = authed_jira)
				for epic in linked_epic_dataset:
					epic_hash[epic['key']] = epic
				for issue in dataset:
					for linked_issue in issue['issuelinks']:
						if linked_issue['key'] in epic_hash and 'issuetype' in linked_issue and linked_issue['issuetype'] == 'Epic':
							linked_issue['summary'] = epic_hash[linked_issue['key']]['summary']
							linked_issue['priority'] = epic_hash[linked_issue['key']]['priority']
							linked_issue['status'] = epic_hash[linked_issue['key']]['status']
			if query_epic_set is not None:
				#threads = []
				# for epic_key in query_epic_set:
				# 	thread = threading.Thread(target = threaded_get_epic_link_query_results, args = (epic_key, epic_link_hash, authed_jira))
				# 	thread.start()
				# 	threads.append(thread)
				query_epic_tuple = tuple(query_epic_set)
				epic_link_dataset, _, _, _, _, _ = get_jira_query_results(query_string = '"Epic Link" in {}'.format(query_epic_tuple), threading = True, authed_jira = authed_jira)
				for issue in epic_link_dataset:
					for linked_issue in issue['issuelinks']:
						if 'issuetype' in linked_issue and linked_issue['issuetype'] == 'Epic':
							epic_key = linked_issue['key']
							if epic_key in epic_link_hash:
								epic_link_hash[epic_key].append(issue) 
							else:
								epic_link_hash[epic_key] = [issue]
					
				#epic_link_hash[epic_key] = epic_link_dataset
				# for thread in threads:
				# 	if thread.is_alive():
				# 		logging.debug('{} still alive'.format(thread.getName()))
				# 		thread.join()
				# 		logging.debug('{} joined {}'.format(thread.getName(), threading.currentThread().getName()))
				for issue in dataset:
					if issue['key'] in epic_link_hash:
						for epic_link_issue in epic_link_hash[issue['key']]:
							issue['issuelinks'].append(epic_link_issue)
	return render_template('index.html', form=form, dataset=dataset, links=links, query_list=query_list)

# def threaded_get_epic_link_query_results(epic_key, epic_link_hash, authed_jira):
# 	epic_link_dataset, _, _, _, _, _ = get_jira_query_results(query_string = '"Epic Link" = "{}"'.format(epic_key), threading = False, authed_jira = authed_jira)
# 	epic_link_hash[epic_key] = epic_link_dataset

@app.route('/health', methods=['GET'])
def health():
	return 'JIRA-GRAPH-VIZ Online' 

