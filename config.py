import os

class Config(object):
  SECRET_KEY = os.environ.get('JIRA_GRAPH_VIZ_KEY') or '2mdfYZRmyFf5EyziWghe'
