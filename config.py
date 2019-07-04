import os

class Config(object):
  # this key is required by flask to run - however as this app does not have users per se
  # this key is not actually relevant to the functioning or security of the app
  SECRET_KEY = os.environ.get('JIRA_GRAPH_VIZ_KEY') or '2mdfYZRmyFf5EyziWghe'
