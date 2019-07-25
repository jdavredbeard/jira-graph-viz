jira-graph-viz is a flask app that provides a force directed graph visualization of jira ticket data built in d3. It is served with gunicorn and has a multi-threaded backend to get large queries from the jira api faster.

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
- Radio buttons toggle visibility of all linked nodes that are not selected by the jira query.
- Nodes are draggable to allow for reorganization.
- On mouseover, node color changes to orange and tooltip with basic ticket information is shown.


Visual Encoding:
- ticket nodes selected by the query have a black border; linked ticket nodes not selected by the query have no border
- ticket nodes are color coded by status: 
- ticket status is also encoded as the radius of the ring to which tickets of a certain status are attracted in the force simulation, where `height` is the height of the svg containing the visualization:
- links between ticket nodes are color coded by link type:
- node radius is coded by issuetype:

Configuring jira-graph-viz for your jira instance:
By default, jira-graph-viz pulls data from Atlassian's public service desk jira at https://jira.atlassian.com.

- To point jira-graph-viz at your jira instance, edit `instance/config.ini` 
  - replace `url` field value with the base url of your jira instance
  - enter authenication details in the `username` and `password` fields
- in `jira_graph_viz/static/constants.js`:
    - update `STATUSCOLORS` dictionary with each ticket status from your instance and the color you want associated with them. 
    - update`RADIALFORCERADIUS` dictionary with each ticket status from your instance and the associated radial force radius you want associated with it (meaning, the radius of the circle to which tickets of that status should be attracted) 
    - update `LINKCOLORS` dictionary with each type of links from your instance and the color you want associated with it
    - update `NODERADIUS` dictionary with each ticket type from your instance and the radius of the circle representing that ticket that you want associated with it
