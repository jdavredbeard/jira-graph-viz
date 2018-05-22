# jira-graph-viz
This project is a webapp that provides a graph visualization of jira queries using d3 with a python backend. It is still under construction!

To view the project, just open index.html in your browser. There are no dependencies to download. 

Index.html is currently running on mock data. 

To run sprintquery.py, create a file called config.ini in the project directory like so:
```
[Basic]
url: https://elsevier-healthsolutions.atlassian.net

[Auth]
username: <jira username>
password: <jira password>
```
Current Functionality:
- page loads with nodes representing tickets from jira query and lines representing links between linked tickets within the query
- jira key labels are links to jira tickets
- clicking nodes will add/remove linked issues that are not contained in the jira query
- nodes are draggable
- on mouseover, node color changes to orange
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

To Do:
- visually encode issuetype with shape of nodes (square, circle, triangle, pentagon, etc)
- modal on mouseover of node - show data pulled in by sprintquery
- add textbox and button to enter query
- create endpoint for frontend to hit to run query
- add legend for colors and shapes
