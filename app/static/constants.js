
// Feel free to add to or modify these to suite your needs.
// If a node has property data that is not represented in these constants objects,
// they will be given default values.

// The base url of the jira server where you keep your tickets - the keys displayed belowed the nodes will link to the
// tickets using this url
const JIRA_BASE_URL = "https://jira.atlassian.com";

// Defines the size of the svg that displays the visualization.
const height = 1600 + querySet.size * 5;
const width = 1600 + querySet.size * 5;

// Defines the colors of the nodes based on their status
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

// Defines the radius of the ring to which nodes with a given status are attracted in
// the force simulation.

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

// Defines the color of the lines between nodes, representing the type of link or relationship
// between them.

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

// Defines the radius of the node representing tickets given a certain ticket type.

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
