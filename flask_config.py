import os

class Config(object):
  SECRET_KEY = os.environ.get('CSRF_KEY')