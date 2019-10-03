from flask import Flask
from flask_config import Config

jira_graph_viz = Flask(__name__)
jira_graph_viz.config.from_object(Config)

from jira_graph_viz import views
