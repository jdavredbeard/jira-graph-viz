from flask import render_template, flash
from flask import request
from app import app
from app.forms import QueryForm
from app.jiraquery import get_jira_query_results
from app.jiraquery import get_jira_auth
from app.jiraquery import get_jira_auth_no_creds
from app.jiraquery import get_jira_auth_no_server_info
import urllib
from sqlalchemy import create_engine
import pandas as pd

@app.route('/', methods=['GET','POST'])
@app.route('/index', methods=['GET','POST'])
def index():
	form = QueryForm()
	query = request.args.get('query')

	if form.validate_on_submit():
		flash('Query submitted: {}'.format(form.query.data))
		return submit_query(form.query.data)
	elif query:
		flash('Query submitted: {}'.format(query))
		return submit_query(query)
	else:
		return displayHome()

@app.route('/health', methods=['GET'])
def health():
	return 'JIRA-GRAPH-VIZ Online'

@app.route('/caliper-queries', methods=['GET'])
def caliper_queries():
	return displayCaliperQueries()

def submit_query(query):
	authed_jira = get_jira_auth()
	# authed_jira = get_jira_auth_no_server_info()
	# authed_jira = get_jira_auth_no_creds()
	dataset, links, query_list, linked_epic_query_string, query_epic_set, error = get_jira_query_results(
		query_string=query, threading=True, authed_jira=authed_jira)
	if error is not None:
		flash('Error Code: {} - {}'.format(error.status_code, error.text))
	else:
		addLinkedEpicsToDatasetLinks(dataset, linked_epic_query_string, authed_jira)
		addChildrenOfEpicsInQueryEpicSetToDataset(dataset, query_epic_set, authed_jira)	
		flash('Issues in query results: {}'.format(len(dataset)))
		url = request.url_root + "index?query=" + urllib.parse.quote(str(query))
		flash('Share this jira-graph-viz: {}'.format(url))

	form = QueryForm()
	form.query.data = query
	return render_template('index.html', form=form, dataset=dataset, links=links, query_list=query_list)

def addChildrenOfEpicsInQueryEpicSetToDataset(dataset, query_epic_set, authed_jira):
	if query_epic_set:
		epic_link_hash = {}
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

def addLinkedEpicsToDatasetLinks(dataset, linked_epic_query_string, authed_jira):
	epic_hash = {}
	if linked_epic_query_string != 'issuekey in ()':
		flash('Linked Epic query submitted: {}'.format(linked_epic_query_string))
		#get data for epics that are 'linked' to tickets in initial query and add them as links
		linked_epic_dataset, _, _, _, _, _ = get_jira_query_results(query_string=linked_epic_query_string,
																	threading=True, authed_jira=authed_jira)

		for epic in linked_epic_dataset:
			if 'key' in epic:
				epic_hash[epic['key']] = epic
		for issue in dataset:
			for linked_issue in issue['issuelinks']:
				if linked_issue['key'] in epic_hash and 'issuetype' in linked_issue and linked_issue[
					'issuetype'] == 'Epic':
					if 'summary' in epic_hash[linked_issue['key']]:
						linked_issue['summary'] = epic_hash[linked_issue['key']]['summary']
					if 'priority' in epic_hash[linked_issue['key']]:
						linked_issue['priority'] = epic_hash[linked_issue['key']]['priority']
					if 'status' in epic_hash[linked_issue['key']]:
						linked_issue['status'] = epic_hash[linked_issue['key']]['status']

def displayHome():
	dataset = {}
	links = {}
	query_list = []
	return render_template('index.html', form=QueryForm(), dataset=dataset, links=links, query_list=query_list)

def displayCaliperQueries():
	query = connectToRedshift()
	print(query)
	return render_template('caliperQueries.html', query=query)

def connectToRedshift():
	redshift_user = 'jdavenport'
	redshift_pwd = 'Analytics123'

	#connecting to REDSHIFT
	redshift_engine = create_engine('postgresql://'
									+ redshift_user
									+':'
									+ redshift_pwd
									+'@localhost:55000/analytics')


	return pd.read_sql_query('''
	SELECT assignable_month, SUM(lesson_assigned) as lessons_assigned,
       SUM(naq_assigned) as non_adaptive_quizzes_assigned,
       SUM(skill_assigned) as skills_assigned,
       SUM(simulation_assigned) as simulations_assigned

FROM
    (SELECT course_section_id,  assignable_id, assignable_type, assignable_due_date,

            CASE WHEN (to_char(to_timestamp (date_part('month',  assignable_due_date)::text, 'MM'), 'Month')) = 'January' then '01. January'
                 WHEN (to_char(to_timestamp (date_part('month',  assignable_due_date)::text, 'MM'), 'Month')) = 'February' then '02. February'
                 WHEN (to_char(to_timestamp (date_part('month',  assignable_due_date)::text, 'MM'), 'Month')) = 'March' then '03. March'
                 WHEN (to_char(to_timestamp (date_part('month',  assignable_due_date)::text, 'MM'), 'Month')) = 'April' then '04. April'
                 WHEN (to_char(to_timestamp (date_part('month',  assignable_due_date)::text, 'MM'), 'Month')) = 'May' then '05. May'
                 WHEN (to_char(to_timestamp (date_part('month',  assignable_due_date)::text, 'MM'), 'Month')) = 'June' then '06. June'
                 WHEN (to_char(to_timestamp (date_part('month',  assignable_due_date)::text, 'MM'), 'Month')) = 'July' then '07. July'
                 WHEN (to_char(to_timestamp (date_part('month',  assignable_due_date)::text, 'MM'), 'Month')) = 'August' then '08. August'
                 WHEN (to_char(to_timestamp (date_part('month',  assignable_due_date)::text, 'MM'), 'Month')) = 'September' then '09. September'
                 WHEN (to_char(to_timestamp (date_part('month',  assignable_due_date)::text, 'MM'), 'Month')) = 'October' then '10. October'
                 WHEN (to_char(to_timestamp (date_part('month',  assignable_due_date)::text, 'MM'), 'Month')) = 'November' then '11. November'
                 WHEN (to_char(to_timestamp (date_part('month',  assignable_due_date)::text, 'MM'), 'Month')) = 'December' then '12. December'
                 ELSE 'WTF' END  as assignable_month,


            SUM(case when (assignable_type = 'simulation') then 1 else 0 end) as simulation_assigned,

            SUM(case when (assignable_type = 'lesson') then 1 else 0 end) as lesson_assigned,

            SUM(case when (assignable_type = 'exam') then 1 else 0 end) as naq_assigned,

            SUM(case when (assignable_type = 'skill') then 1 else 0 end) as skill_assigned,

            SUM(case when (assignable_type = 'MASTERY') then 1 else 0 end) as mastery_assigned,

            SUM(case when (assignable_type = 'QUIZ_BY_QUESTION') then 1 else 0 end) as qbq_assigned,

            SUM(case when (assignable_type = 'STANDARD') then 1 else 0 end) as custom_assigned

     FROM
         (SELECT *,
                 row_number() over(partition by assignable_id, course_section_id order by a.assignment_created_ts desc) as latest_event
          FROM
              (SELECT  a.created_ts as assignment_created_ts,
                       a.course_section_id,
                       a.assignable_id,
                       a.assignable_type ,
                       CAST(due_dt at time zone 'utc' at time zone 'est5edt' as TIMESTAMP) as assignable_due_date
               FROM            assignable_event_dimension a
               WHERE  a.assignable_type in ('lesson', 'skill','simulation','exam')
                 and education_app_id in ('skills-viewer', 'content-viewer')

                 and due_dt at time zone 'utc' at time zone 'est5edt' BETWEEN '2019-01-01' and '2019-06-27'

               GROUP BY a.created_ts,
                        a.course_section_id,
                        a.assignable_id,
                        a.assignable_type,
                        a.due_dt ) a )a
     WHERE latest_event = 1
     GROUP BY course_section_id,assignable_id, assignable_type, assignable_due_date)a
GROUP BY assignable_month
ORDER BY assignable_month
	
	''',redshift_engine).to_csv(index=False)