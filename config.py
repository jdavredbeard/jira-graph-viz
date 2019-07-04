import os

class Config(object):
  # this key is required by flask to run in order to encrypt session data -
  # however as this app does not have users per se
  # it is not actually relevant to the security of the app, and thus
  # commiting it is not a security risk at this time
  SECRET_KEY = os.environ.get('JIRA_GRAPH_VIZ_KEY') or '2mdfYZRmyFf5EyziWghe'
