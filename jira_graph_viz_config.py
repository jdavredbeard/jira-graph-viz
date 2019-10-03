import configparser
import os
import jira


class Configs:
    def __init__(self):
        self._config = self._get_config()
        self._username = self._config.get('Auth', 'username')
        self._password = self._config.get('Auth', 'password')
        self._url = self._config.get('Basic', 'url')

    def _get_config(self):
        SCRIPT_DIR = os.path.dirname(os.path.realpath(__file__))

        config = configparser.ConfigParser()
        config.read(SCRIPT_DIR + '/instance/config.ini')
        return config

    def get_jira(self):
        if self._username != '' and self._password != '':
            return self.get_authed_jira()
        else:
            return self.get_unauthed_jira()

    def get_authed_jira(self):
        return jira.JIRA(basic_auth=(self._username, self._password), options={'server': self._url})

    def get_unauthed_jira(self):
        return jira.JIRA(self._url)

    def get_url(self):
        return self._url

