
def parse_data_from_jira_api_response(issues):
    tickets, links_in_tickets, query_list = parse_issues(issues)
    return tickets, links_in_tickets, query_list, None


def parse_issues(issues):
    query_epic_set = set()
    query_set = set()
    tickets = []
    all_links = []

    for issue in issues:
        parsed_issue = create_parsed_issue(issue)

        links = issue.fields.issuelinks
        subtasks = issue.fields.subtasks
        link_data = []

        add_issue_links_to_link_data(issue, links, link_data, all_links)
        add_parent_to_link_data(issue, link_data, all_links)
        add_subtasks_to_link_data(issue, subtasks, link_data, all_links)

        parsed_issue = add_links_to_parsed_issue(parsed_issue, link_data)

        tickets.append(parsed_issue)

        if issue.fields.issuetype.name == 'Epic':
            query_epic_set.add(issue.key)

        query_set.add(issue.key)

    links_in_tickets = add_links_in_query_set_to_links_in_tickets(all_links, query_set)
    query_list = list(query_set)
    return tickets, links_in_tickets, query_list


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


def add_links_in_query_set_to_links_in_tickets(all_links, query_set):
    links_in_tickets = []
    for link in all_links:
        if link['source'] in query_set and link['target'] in query_set:
            link['addedBy'] = 'query'
            links_in_tickets.append(link)
    return links_in_tickets


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