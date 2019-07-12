jira-graph-viz is a flask app that provides a force directed graph visualization of jira ticket data built in d3.

Visit the app at http://jira-graph-viz-automation.apps.els-ols.com/

To run it locally:

Make sure you have python and pip installed. Starting a virtualenv is recommended.

After cloning the repo:
- create a `.env` file in the project directory and set a cryptographic key for the Flask-WTF webform with `export JIRA-GRAPH-VIZ-KEY={your-secret-key}`
- source the `.env` file
- `pip install -r requirements.txt`
- `gunicorn jira-graph-viz`
- Open `localhost:8000` in browser

Using jira-graph-viz:
- Enter a JQL query in the text field and click 'submit'. The page loads with graph nodes representing tickets from the jira query and edges representing links between tickets. The subtask and epic-link relationships are treated as links as well.
- Jira key labels (ex. EAQ-125) are hyperlinks to jira tickets.
- Clicking a node will toggle visibility of nodes linked to that node that are not selected by the jira query
- Radio buttons toggle visibility of all linked nodes that are not selected by the jira query.
- Nodes are draggable to allow for visual reorganization.
- On mouseover, node color changes to orange and tooltip with basic ticket information is shown.


Visual Encoding:
- ticket nodes selected by the query have a black border; linked ticket nodes not selected by the query have no border
- ticket nodes are color coded by status: 
```
const STATUSCOLORS = {
                "Draft": "#E8E8E8", //light grey
                "To Do": "#8e8e93", //grey
                "Icebox": "aqua",
                "In Progress": "#ffcc00", //yellow
                "Code Review": "#ff8300", //bright orange
                "Blocked": "red",
                "Testing Failed": "purple",
                "Ready for Testing": "#007aff", //dark blue
                "Ready for Acceptance": "#0D98BA", //blue-green
                "Ready for Production": "#0D98BA", //blue-green
                "Ready for Release": "#0D98BA", //blue-green
                "Ready to Deploy": "#0D98BA", //blue-green
                "Deployed": "#4cd964", // green
                "Done": "#4cd964", // green
                "Testing Passed": "#4cd964", // green
                "Released": "#4cd964", //green
                "Completed": "#4cd964", //green
                "Complete": "#4cd964", //green
            }
```
- ticket status is also encoded as the radius of the ring to which tickets of a certain status are attracted in the force simulation, where `height` is the height of the svg containing the visualization:
```
const RADIALFORCERADIUS = {
                "Draft": 0,
                "To Do": height * 0.05,
                "Icebox": height * 0.3,
                "In Progress": height * 0.1,
                "Code Review": height * 0.1,
                "Blocked": 0,
                "Testing Failed": 0,
                "Ready for Testing": height * 0.15,
                "Ready for Acceptance": height * 0.2,
                "Ready for Production": height * 0.2,
                "Ready for Release": height * 0.2,
                "Ready to Deploy": height * 0.2,
                "Deployed": height * 0.25, // green
                "Done": height * 0.25, // green
                "Testing Passed": height * 0.25, // green
                "Released": height * 0.25, //green
                "Completed": height * 0.25, //green
                "Complete": height   * 0.25, //green
            }
```
- links between ticket nodes are color coded by link type:
```
const LINKCOLORS = {
                "Relates": "green",
                "Related": "green",
                "Dependency": "orange",
                "Blocks": "red",
                "Bonfire Testing": "purple", // bonfire testing = discovered while testing
                "Issue Split": "#007aff", // dark blue
                "Cloners": "#5ac8fa", // light blue
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
                    "Content": 25,
                    "Design": 25,
                    "QA Task": 25,
                    "Bug": 15,
                    "Sub-task": 10,
                    "QA Test Case": 5,
                    "Task": 25
                }
```

To Do:

- add legend for colors and shapes
- add support for showing more levels of linked tickets
