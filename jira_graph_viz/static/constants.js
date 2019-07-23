
// Feel free to add to or modify these to suite your needs.
// If a node has property data that is not represented in these constants objects,
// they will be given default values.

// The base url of the jira server where you keep your tickets - the keys displayed belowed the nodes will link to the
// tickets using this url
const JIRA_BASE_URL = 'https://jira.atlassian.com';

// Defines the size of the svg that displays the visualization.
const height = 1600 + querySet.size * 5;
const width = 1600 + querySet.size * 5;

// Defines the colors of the nodes based on their status

const STATUSCOLORS = {
    // suggestion statuses
    'Gathering Interest': '#8e8e93', //grey
    
    // bug statuses
    'Open': '#8e8e93', //grey
    'Needs Verification': '#ffcc00', //yellow
    'Verified': '#ff8300', //bright orange
    'Awaiting Development': 'red',
    'Awaiting Soak': 'purple',
    'In Progress': '#007aff', //dark blue
    'Technical Review': '#0D98BA', //blue-green
    'Soaking': '#0D98BA', //blue-green
    'Resolved': '#4cd964', // green
    'Closed': '#4cd964', // green
}

// Defines the radius of the ring to which nodes with a given status are attracted in
// the force simulation.

const RADIALFORCERADIUS = {
    'Open': 0,
    'Needs Verification': height * 0.05,
    'Verified': height * 0.1,
    'Awaiting Development': height * 0.1,
    'Awaiting Soak': height * 0.15,
    'In Progress': height * 0.2,
    'Technical Review': height * 0.25,
    'Soaking': height * 0.28,
    'Resolved': height * 0.3,
    'Closed': height * 0.33
}

// Defines the color of the lines between nodes, representing the type of link or relationship
// between them.

const LINKCOLORS = {
    'Relates': 'green',
    'Related': 'green',
    'Dependency': 'orange',
    'Blocks': 'red',
    'Bonfire Testing': 'purple', // bonfire testing = discovered while testing
    'Issue Split': '#007aff', // dark blue
    'Cloners': '#5ac8fa', // light blue
    'subtask': 'black',
    'parent': 'black'
}

// Defines the radius of the node representing tickets given a certain ticket type.

const NODERADIUS = {
    'Epic': 40,
    'Story': 25,
    'Technical Story': 25,
    'Content': 25,
    'Design': 25,
    'QA Task': 25,
    'Bug': 15,
    'Sub-task': 10,
    'QA Test Case': 5,
    'Task': 25,
}
