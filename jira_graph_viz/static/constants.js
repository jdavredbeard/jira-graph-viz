

// The base url of the jira server where you keep your tickets - the keys displayed below the nodes will link to the
// tickets using this url
const JIRA_BASE_URL = jiraBaseUrl + '/browse/';


// Visualization sizing constants:
const HEIGHT = 1600 + querySet.size * 5;
const WIDTH = 1600 + querySet.size * 5;
const X_CENTER = WIDTH / 2;
const Y_CENTER = HEIGHT / 2;


// force simulation constants:
const FORCE_MANY_BODY_STRENGTH = -1000;
const FORCE_COLLIDE_RADIUS = 45;
const FORCE_RADIAL_STRENGTH = 0.5;
const RESTART_ALPHA = 0.8;
const RADIAL_FORCE_RADIUS_DEFAULT = 0;

// drag-drop constants:
const DRAG_ALPHA_TARGET = 0.6;
const DROP_ALPHA_TARGET = 0;


// key text constants:
const KEY_TEXT_DX_OFFSET_MULTIPLIER = 3;
const KEY_TEXT_DY_OFFSET = 15;
const KEY_TEXT_DY_OFFSET_DEFAULT = 25;
const KEY_TEXT_FONT_SIZE = 12;


// node visualization constants:
const NODE_RADIUS_DEFAULT = 10;
const NODE_BORDER_WIDTH = 3;


// link visualization constants:
const LINK_LINE_WIDTH = 3;
const LINK_LINE_DASH_ARRAY = [5,4];
const LINK_LINE_OPACITY = 0.8;


// mouse-over/mouse-out/tool-tip constants:
const MOUSE_OVER_DURATION = 200;
const MOUSE_OVER_OPACITY = 0.9;
const TOOL_TIP_Y_OFFSET = 28;
const MOUSE_OUT_DURATION = 500;
const MOUSE_OUT_OPACITY = 0;




// Visual Encoding constants:
// Feel free to add to or modify these to suite your needs.
// If a node has property data that is not represented in these constants objects,
// they will be given default values.

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
    'Needs Verification': HEIGHT * 0.05,
    'Verified': HEIGHT * 0.1,
    'Awaiting Development': HEIGHT * 0.1,
    'Awaiting Soak': HEIGHT * 0.15,
    'In Progress': HEIGHT * 0.2,
    'Technical Review': HEIGHT * 0.25,
    'Soaking': HEIGHT * 0.28,
    'Resolved': HEIGHT * 0.3,
    'Closed': HEIGHT * 0.33
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


