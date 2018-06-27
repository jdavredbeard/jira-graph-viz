This project is a webapp that provides a graph visualization of jira queries using d3 with a python/flask backend used to host the page, contact the jira api, and parse the data. It is still under construction!

Visit the app at http://jira-graph-viz-automation.apps.els-ols.com/

To run it locally:

Make sure you have python and pip installed.

After cloning the repo:
- `pip install -r requirements.txt`
- `export FLASK_APP=jira-graph-viz.py`
- `flask run`
- Open `localhost:5000` in browser

Current Functionality:
- enter JQL query in box- page loads with nodes representing tickets from jira query and lines representing links between linked tickets within the query. The subtask relationship is treated as a link in this case.
- jira key labels (ex. EAQ-125)  are hyperlinks to actual jira tickets
- clicking nodes will add/remove linked issues and subtasks that are not contained in the jira query
- use radio buttons toggle between viewing all linked tickets/viewing only linked tickets that are selected by query
- nodes are draggable
- on mouseover, node color changes to orange

Visual Encoding:
- ticket nodes selected by the query have a black border; linked ticket nodes not selected by the query have no border
- ticket nodes are color coded by status: 
```
const STATUSCOLORS = {
                "To Do": "#8e8e93", //grey
                "Icebox": "aqua",
                "In Progress": "#ffcc00", //yellow
                "Code Review": "orange",
                "Blocked": "red",
                "Testing Failed": "purple",
                "Ready for Testing": "#007aff", //dark blue
                "Ready for Acceptance": "#009F6B", //dark green
                "Done": "#4cd964", // green
                "Testing Passed": "#4cd964", // green
                "Ready for Production": "#4cd964", //green
                "Completed": "#4cd964", //green
            }
```
- links between ticket nodes are color coded by link type:
```
const LINKCOLORS = {
                "Relates": "green", 
                "Related": "green", 
                "Dependency": "orange", 
                "Blocks": "red",
                "Bonfire Testing": "purple", //discovered while testing
                "Issue Split": "#007aff", //dark blue
                "Cloners": "#5ac8fa", //light blue
                "subtask": "black",
                "parent": "black"
            }
```
- node radius is coded by issuetype:
```
const NODERADIUS = {
                    "Epic": 40,
                    "Story": 25,
                    "Technical Story": 25,
                    "Design": 25,
                    "Bug": 15,
                    "Sub-task": 10,
                    "QA Task": 10,
                    "QA Test Case": 5
            }
```

To Do:

- modal on mouseover of node - show summary, project, assignee, status, sprint, epic
- add legend for colors and shapes
- add support for showing more levels of linked tickets
