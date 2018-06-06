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
  if form.validate_on_submit():
  	flash('Query submitted: {}'.format(form.query.data))
  	dataset, links, query_list = get_jira_query_results(form.query.data)
  return render_template('index.html', form=form, dataset=dataset, links=links, query_list=query_list)



