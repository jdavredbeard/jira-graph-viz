## jira-graph-viz
`jira-graph-viz` is a flask app that provides a force directed graph visualization of jira ticket data built in d3.  
`jira-graph-viz` can be useful to get a high level view of work in a sprint, or or how work is connected to upstream or downstream dependencies.  
`jira-graph-viz` is served with gunicorn and has a multi-threaded backend to get large queries from the jira api faster.   
  
### To run it locally:

Make sure you have python and pip installed. Starting a virtualenv is recommended.

After cloning the repo:
- set your Jira api token with `export JIRA_API_TOKEN={your-jira-api-token}`
- set your Jira base url with `export JIRA_BASE_URL={your-jira-base-url}` By default, jira-graph-viz pulls data from Atlassian's public service desk jira at https://jira.atlassian.com.
- `pip install -r requirements.txt`
- `gunicorn jira-graph-viz`
- Open `localhost:8000` in browser

### Using `jira-graph-viz`:
- Enter a JQL query in the text field and click 'submit'. The page loads with graph nodes representing tickets from the jira query and edges representing links between tickets. The subtask and epic-link relationships are treated as links as well.
- Jira key labels (ex. EAQ-125) are hyperlinks to jira tickets.
- Radio buttons toggle visibility of all tickets that are linked to the tickets selected by the query.
- Nodes are draggable to allow for reorganization.
- On mouseover, ticket color changes to orange and tooltip with basic ticket information is shown.


### Visual Encoding:
- tickets selected by the query have a black border; linked tickets not selected by the query have no border.
- tickets are color coded by status. tickets of different statuses also organize themselves into concentric rings.
- links between tickets are color coded by link type
- node radius (radius of the circle that represents a ticket) is coded by issuetype.
- To configure the visualization for your jira data, in `jira_graph_viz/static/constants.js`:
    - update `STATUSCOLORS` dictionary with each ticket status from your jira instance and the color you want associated with them. 
    - update`RADIALFORCERADIUS` dictionary with each ticket status from your jira instance and the associated radial force radius you want associated with it (meaning, the radius of the concentric circle to which tickets of that status should be attracted) 
    - update `LINKCOLORS` dictionary with each type of links from your instance and the color you want associated with it
    - update `NODERADIUS` dictionary with each ticket type from your instance and the radius of the circle representing that ticket that you want associated with it
