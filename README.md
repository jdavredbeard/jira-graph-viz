# jira-graph-viz
This project is a webapp that provides a graph visualization of jira queries using d3 with a python/flask backend used to host the page, contact the jira api, and parse the data. It is still under construction!

To run:

After cloning the repo:
`pip install -r requirements.txt`
`flask run`
Open `localhost:5000`

Current Functionality:
- page loads with nodes representing tickets from jira query and lines representing links between linked tickets within the query
- subtasks of tickets within query are represented as links (see color coding of links below)
- jira key labels (ex. EAQ-125)  are hyperlinks to actual jira tickets
- clicking nodes will add/remove linked issues and subtasks that are not contained in the jira query
- nodes are draggable
- on mouseover, node color changes to orange
- tickets within the original query have a black border
- nodes are color coded by status: 
```
colors = {
                "To Do": "#8e8e93", //grey
                "Icebox": "aqua",
                "In Progress": "#ffcc00", //yellow
                "Code Review": "orange",
                "Blocked": "red",
                "Testing Failed": "purple",
                "Ready for Testing": "#007aff", //dark blue
                "Ready for Acceptance": "#5ac8fa", //light blue
                "Done": "#4cd964" // green
              }
```
- links between tickets are color coded by link type:
```
colors = {	
		"Relates": "green",
                "Related": "green",
                "Dependency": "orange", 
                "Blocks": "red",
                "Bonfire Testing": "purple",
                "Issue Split": "#007aff", //dark blue
                "Cloners": "#5ac8fa", //light blue
                "subtask": "black"
              }
```

To Do:

- modal on mouseover of node - show data pulled in by sprintquery
- add legend for colors and shapes
- add support for epic links
- add option to group by epics
- add support for showing more levels of linked tickets
