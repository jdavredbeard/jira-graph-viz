from flask import render_template, flash
from app import app
from app.forms import QueryForm
from app.jiraquery import get_jira_query_results


@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
def index():
  form = QueryForm()
  dataset = {}
  links = {}
  query_list = []
  epic_dataset = []
  epic_links = []
  epic_query_list = []
  epic_query_string = ""
  epic_hash = {}

  if form.validate_on_submit():
  	flash('Query submitted: {}'.format(form.query.data))
  	dataset, links, query_list, epic_query_string, error = get_jira_query_results(form.query.data)
  	if error is not None:
  		flash('Error Code: {} - {}'.format(error.status_code, error.text))
  	else:
  		flash('Linked Epic query submitted: {}'.format(epic_query_string))
	  	epic_dataset, epic_links, epic_query_list, epic_query_string, error = get_jira_query_results(epic_query_string)
	  	for epic in epic_dataset:
	  		epic_hash[epic['key']] = epic
	  	for issue in dataset:
	  		for linked_issue in issue['issuelinks']:
	  			if linked_issue['key'] in epic_hash and linked_issue['issuetype'] == 'Epic':
	  				linked_issue['summary'] = epic_hash[linked_issue['key']]['summary']
	  				linked_issue['priority'] = epic_hash[linked_issue['key']]['priority']
	  				linked_issue['status'] = epic_hash[linked_issue['key']]['status']
	  				#print(linked_issue)
  #print(dataset)

  return render_template('index.html', form=form, dataset=dataset, links=links, query_list=query_list)



