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

from flask import render_template
from flask import request
from jira_graph_viz import jira_graph_viz
from jira_graph_viz.forms import QueryForm
from jira_graph_viz.query_controller import submit_query
from jira_graph_viz.query_controller import submit_query_with_link_levels
import os

@jira_graph_viz.route('/', methods=['GET','POST'])
@jira_graph_viz.route('/index', methods=['GET','POST'])
def index():
	form = QueryForm()
	query = request.args.get('query')

	dataset = []
	links = []
	query_list = []

	jira_base_url = os.environ.get('JIRA_BASE_URL','https://jira.atlassian.com')

	link_levels = 4

	if form.validate_on_submit():
		dataset,links,query_list = submit_query_with_link_levels(form.query.data, link_levels)
	elif query:
		dataset,links,query_list = submit_query(query)
	return render_template('index.html',
						   form = QueryForm(),
						   dataset = dataset,
						   links = links,
						   query_list = query_list,
						   jira_base_url = jira_base_url)


@jira_graph_viz.route('/health', methods=['GET'])
def health():
	return 'JIRA-GRAPH-VIZ Online'
