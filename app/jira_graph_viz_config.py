import configparser
import os
import jira


class Configs:
    def __init__(self):
        self._config = self.get_config()
        self._username = self._config.get('Auth', 'username')
        self._password = self._config.get('Auth', 'password')
        self._url = self._config.get('Basic', 'url')
        self.authed_jira = jira.JIRA(self._url, basic_auth=(self._username, self._password))

    def get_config(self):
        SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

        config = configparser.ConfigParser()
        config.read(SCRIPT_DIR + '/' + 'config.ini')
        return config
