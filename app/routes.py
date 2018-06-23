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

  if form.validate_on_submit():
  	flash('Query submitted: {}'.format(form.query.data))
  	dataset, links, query_list, epic_query_string, error = get_jira_query_results(form.query.data)
  	# #epic_dataset, epic_links, epic_query_list, epic_query_string = get_jira_query_results(epic_query_string)
  	# for issue in epic_dataset:
  	# 	dataset.append(issue)
  	if error is not None:
  		flash('Error Code: {} - {}'.format(error.status_code, error.text))

  return render_template('index.html', form=form, dataset=dataset, links=links, query_list=query_list)



