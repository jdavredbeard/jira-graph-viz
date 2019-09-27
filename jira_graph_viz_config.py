# Copyright 2019 Elsevier Inc.

# This file is part of jira-graph-viz.

# jira-graph-viz is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# jira-graph-viz is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with jira-graph-viz.  If not, see <https://www.gnu.org/licenses/>

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

