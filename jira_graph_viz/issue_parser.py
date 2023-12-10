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

def parse_data_from_jira_api_response(issues):
    tickets, links_in_tickets, query_list, linked_epic_query_string, query_epic_set = parse_issues(issues)
    return tickets, links_in_tickets, query_list, linked_epic_query_string, query_epic_set, None


def parse_issues(issues):
    linked_epic_set = set()
    query_epic_set = set()
    query_set = set()
    tickets = []
    all_links = []
    next_level_set = set()

    for issue in issues:
        parsed_issue = create_parsed_issue(issue)

        links = issue.fields.issuelinks
        subtasks = issue.fields.subtasks
        link_data = []

        add_issue_links_to_link_data(issue, links, link_data, all_links)
        add_parent_to_link_data(issue, link_data, all_links)
        add_subtasks_to_link_data(issue, subtasks, link_data, all_links)
        add_epic_to_link_data(issue, linked_epic_set, link_data, all_links)

        if parsed_issue['key'] not in query_set:
            tickets.append(parsed_issue)

        tickets.extend(link_data)

        link_data_keys = [link['key'] for link in link_data]

        next_level_set = next_level_set.union(set(link_data_keys))

        query_set.add(issue.key)

    links_in_tickets, tickets_next_level = add_links_in_query_set_to_links_in_tickets(all_links, query_set, next_level_set, link_level)

    query_set = query_set.union(next_level_set)
    return tickets, links_in_tickets, query_set, tickets_next_level


def create_parsed_issue(issue):
    return parse_fields_from_issue(issue,
                                   fields = [{"sourceName": ("key",), "targetName": "key"},
                                             {"sourceName": ("raw", "fields", "summary"), "targetName": "summary"},
                                             {"sourceName": ("raw", "fields", "status","name"), "targetName": "status"},
                                             {"sourceName": ("raw", "fields", "issuetype", "name"), "targetName": "issuetype"},
                                             {"sourceName": ("raw","fields", "priority", "name"), "targetName": "priority"},
                                             {"sourceName": ("raw", "fields", "assignee", "name"), "targetName": "assignee"}])


def create_parsed_inward_issue(issue):
    return parse_fields_from_issue(issue,
                                   fields = [{"sourceName": ("raw", "inwardIssue", "key"), "targetName": "key"},
                                             {"sourceName": ("raw", "inwardIssue", "fields", "summary"), "targetName": "summary"},
                                             {"sourceName": ("raw", "inwardIssue", "fields", "status","name"), "targetName": "status"},
                                             {"sourceName": ("raw", "inwardIssue", "fields", "issuetype", "name"), "targetName": "issuetype"},
                                             {"sourceName": ("raw", "inwardIssue", "fields", "priority", "name"), "targetName": "priority"},
                                             {"sourceName": ("raw", "inwardIssue", "fields", "assignee", "name"), "targetName": "assignee"},
                                             {"sourceName": ("raw", "type", "name"), "targetName": "type"}])


def create_parsed_outward_issue(issue):
    return parse_fields_from_issue(issue,
                                   fields = [{"sourceName": ("raw", "outwardIssue", "key"), "targetName": "key"},
                                             {"sourceName": ("raw", "outwardIssue", "fields", "summary"), "targetName": "summary"},
                                             {"sourceName": ("raw", "outwardIssue", "fields", "status","name"), "targetName": "status"},
                                             {"sourceName": ("raw", "outwardIssue", "fields", "issuetype", "name"), "targetName": "issuetype"},
                                             {"sourceName": ("raw", "outwardIssue", "fields", "priority", "name"), "targetName": "priority"},
                                             {"sourceName": ("raw", "outwardIssue", "fields", "assignee", "name"), "targetName": "assignee"},
                                             {"sourceName": ("raw", "type", "name"), "targetName": "type"}])


def parse_fields_from_issue(sourceIssue, fields):
    parsed_issue = {}
    for field in fields:
        field_value = get_nested(vars(sourceIssue), *field["sourceName"])
        if field_value is not None:
            parsed_issue[field["targetName"]] = field_value
    return parsed_issue


def get_nested(data, *args):
    if args and data:
        element = args[0]
        if element:
            value = data.get(element)
            return value if len(args) == 1 else get_nested(value, *args[1:])


def add_links_to_parsed_issue(parsed_issue, link_data):
    parsed_issue['issuelinks'] = link_data
    return parsed_issue


def add_links_in_query_set_to_links_in_tickets(all_links, query_set, next_level_set, link_level):
    links_in_tickets = []
    tickets_next_level = set()
    for link in all_links:
        if link['source'] in query_set and link['target'] in query_set:
            link['addedBy'] = 'query'
            links_in_tickets.append(link)
        elif link['source'] in query_set and link['target'] in next_level_set:
            link['addedBy'] = '{}, link level {}'.format(link['source'],link_level)
            links_in_tickets.append(link)
            tickets_next_level.add(link['target'])
    return links_in_tickets, tickets_next_level


def add_subtasks_to_link_data(issue, subtasks, link_data, all_links):
    for subtask in subtasks:
        if subtask is not None:
            parsed_subtask = create_parsed_issue(subtask)

            parsed_subtask['type'] = 'subtask'
            link_data.append(parsed_subtask)

            all_links.append({
                'source': issue.key,
                'target': subtask.key,
                'type': 'subtask'
            })


def add_parent_to_link_data(issue, link_data, all_links):
    if 'parent' in vars(issue.fields):
        parent = issue.fields.parent
        parsed_parent = create_parsed_issue(parent)

        parsed_parent['type'] = 'parent'

        link_data.append(parsed_parent)

        all_links.append({
            'source': issue.key,
            'target': parent.key,
            'type': 'parent'
        })


def add_issue_links_to_link_data(issue, links, link_data, all_links):
    for link in links:
        if link is not None:
            if 'inwardIssue' in vars(link):

                parsed_issue = create_parsed_inward_issue(link)
                parsed_issue['direction'] = 'inward'

                all_links.append({
                    'source': issue.key,
                    'target': link.inwardIssue.key,
                    'type': link.type.name,
                    'direction': 'inward'
                })
            elif 'outwardIssue' in vars(link):
                parsed_issue = create_parsed_outward_issue(link)

                parsed_issue['direction'] = 'outward'

                all_links.append({
                    'source': issue.key,
                    'target': link.outwardIssue.key,
                    'type': link.type.name,
                    'direction': 'outward'
                })

            link_data.append(parsed_issue)


def create_linked_epic_query_string(linked_epic_set):
    linked_epic_list = list(linked_epic_set)
    return 'issuekey in (' + ','.join(linked_epic_list) + ')'


def add_epic_to_link_data(issue, linked_epic_set, link_data, all_links):
    # customfield_10007 = epic key
    if "customfield_10007" in vars(issue.fields) and issue.fields.customfield_10007 is not None:

        linked_epic_set.add(issue.fields.customfield_10007)

        data = {
            'issuetype': 'Epic',
            'key': issue.fields.customfield_10007,
        }

        link_data.append(data)

        all_links.append({
            'source': issue.key,
            'target': issue.fields.customfield_10007,
            'type': 'epic parent'
        })