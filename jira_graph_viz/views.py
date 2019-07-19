from flask import render_template, flash
from flask import request
from jira_graph_viz import jira_graph_viz
from jira_graph_viz.forms import QueryForm
from jira_graph_viz.jiraquery import get_jira_query_results
import urllib
from jira_graph_viz_config import Configs

@jira_graph_viz.route('/', methods=['GET','POST'])
@jira_graph_viz.route('/index', methods=['GET','POST'])
def index():
	form = QueryForm()
	query = request.args.get('query')

	jira_configs = Configs()
	jira_connection = jira_configs.get_jira()

	if form.validate_on_submit():
		flash('Query submitted: {}'.format(form.query.data))
		return submit_query(form.query.data, jira_connection)
	elif query:
		flash('Query submitted: {}'.format(query))
		return submit_query(query, jira_connection)
	else:
		return display_home()

@jira_graph_viz.route('/health', methods=['GET'])
def health():
	return 'JIRA-GRAPH-VIZ Online'

def submit_query(query, jira_connection):

	dataset, links, query_list, error = get_jira_query_results(
		query_string=query, threading=True, jira_connection=jira_connection)
	if error is not None:
		flash('Error Code: {} - {}'.format(error.status_code, error.text))
	else:
		flash('Issues in query results: {}'.format(len(dataset)))
		url = request.url_root + "index?query=" + urllib.parse.quote(str(query))
		flash('Share this jira-graph-viz: {}'.format(url))

	form = QueryForm()
	form.query.data = query
	return render_template('index.html', form=form, dataset=dataset, links=links, query_list=query_list)

def display_home():
	dataset = {}
	links = {}
	query_list = []
	return render_template('index.html', form=QueryForm(), dataset=dataset, links=links, query_list=query_list)
