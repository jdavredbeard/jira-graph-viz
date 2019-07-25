import os

class Config(object):
  SECRET_KEY = os.environ.get('JIRA_GRAPH_VIZ_KEY')