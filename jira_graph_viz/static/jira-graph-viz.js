

var svg = d3.select('body').append('svg').attr('width', width).attr('height', height),
    nodeLink = svg.append("g").attr('class', 'nodeLinks').selectAll('line'),
    node = svg.append('g').attr('class', 'nodes').selectAll('circle'),
    keyLink = svg.append('g').attr('class', 'keyLinks').selectAll('a');

// Define the div for the tooltip
var div = d3.select("body").append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);

var linkForce = d3.forceLink()
    .id(function (link) { return link.key })

var simulation = d3.forceSimulation()
    .force('link', linkForce)
    .force('charge', d3.forceManyBody().strength(-1000))
    .force('center', d3.forceCenter(width / 2, height / 2))
    .force('x', d3.forceX())
    .force('y', d3.forceY())
    .force('collision', d3.forceCollide().radius(d => Math.min(NODERADIUS[d.issuetype] * 6, 45)))
    .force('radial', d3.forceRadial(getRadialForceRadiusFromTicketStatus, width / 2, height / 2).strength(.5))
    .on('tick', ticked);

var dragDrop = d3.drag().on('start', function (node) {
    node.fx = node.x
    node.fy = node.y
}).on('drag', function (node) {
    simulation.alphaTarget(0.6).restart()
    node.fx = d3.event.x
    node.fy = d3.event.y
}).on('end', function (node) {
    if (!d3.event.active) {
        simulation.alphaTarget(0)
    }
    node.fx = null
    node.fy = null
});

update();

function update() {

    node = node.data([...dataset], d => d.key);
    node.exit().remove();
    node = node.enter()
        .append('circle')
        .attr('r', getRadiusFromTicketType)
        .attr('fill', getNodeColorFromStatus)
        .attr('stroke', getStrokeColor)
        .attr('stroke-width', 3)
        .merge(node)
        .call(dragDrop)
        .on('mouseover', handleMouseOver)
        .on('mouseout', handleMouseOut)
       // .on('click', handleClick);

    nodeLink = nodeLink.data([...links], d => d.source + ' ' + d.target);
    nodeLink.exit().remove();
    nodeLink = nodeLink.enter()
        .append("line")
        .attr("stroke-width", 3)
        .attr("stroke", getLineColorFromLinkType)
        .attr("stroke-dasharray", [5,4])
        .attr("opacity", .8)
        .merge(nodeLink);

    keyLink = keyLink.data([...dataset], d => d.key);
    keyLink.exit().remove();
    keyLink = keyLink.enter()
        .append('a')
        .attr('href', function(d) { return JIRA_BASE_URL + d.key})
        .attr('target', '_blank')
        .append('text')
        .text(node => node.key)
        .attr("font-family", "Helvetica, sans-serif")
        .attr('font-size', 12)
        .attr('font-weight', 'bold')
        .attr('dx', getDxOffsetFromKeyLength)
        .attr('dy', getKeyTextOffsetFromTicketType)
        .style('cursor', 'pointer')
        .merge(keyLink);

    nestedKeyText = svg.selectAll('text');

    simulation.nodes([...dataset])
    simulation.force('link').links([...links]);
    simulation.alpha(.8).restart();
}

function getDxOffsetFromKeyLength(d) {
    return 0 - (d.key.length * 3)
}

function getKeyTextOffsetFromTicketType(d) {
    if (d.issuetype in NODERADIUS) return NODERADIUS[d.issuetype] + 15;
    else return 25;

}

function getRadiusFromTicketType(d) {
    if (d.issuetype in NODERADIUS) return NODERADIUS[d.issuetype];
    else return 10;

}

function getRadialForceRadiusFromTicketStatus(d) {
    if (d.status in RADIALFORCERADIUS) return RADIALFORCERADIUS[d.status];
    else return 0;
}

function handleMouseOver(d, i) {
    d3.select(this).attr('fill', 'orange');
    div.transition()
        .duration(200)
        .style("opacity", .9);
    div .html("<b>Summary: </b>" + d.summary + "<br/>"  +
        "<b>Priority: </b>" + d.priority + "<br/>" +
        "<b>Assignee: </b>" + d.assignee + "<br/>" +
        "<b>Issuetype: </b>" + d.issuetype + "<br/>" +
        "<b>Status: </b>" + d.status)
        .style("left", (d3.event.pageX) + "px")
        .style("top", (d3.event.pageY - 28) + "px");
}

function handleMouseOut(d, i) {
    d3.select(this).attr('fill', getNodeColorFromStatus);
    div.transition()
        .duration(500)
        .style("opacity", 0);
}

function getStrokeColor(d) {
    if (querySet.has(d.key)) return "black";
    else return getNodeColorFromStatus;
}

function getNodeColorFromStatus(node) {
    if (node.status in STATUSCOLORS) return STATUSCOLORS[node.status];
    else return "black";
}

function getLineColorFromLinkType(link) {
    if (link.type in LINKCOLORS) return LINKCOLORS[link.type];
    else return "black";
}

function ticked() {
    node
        .attr('cx', function (node) { return node.x })
        .attr('cy', function (node) { return node.y });
    nestedKeyText
        .attr('x', function (node) { return node.x })
        .attr('y', function (node) { return node.y });
    nodeLink
        .attr('x1', function (link) { return link.source.x })
        .attr('y1', function (link) { return link.source.y })
        .attr('x2', function (link) { return link.target.x })
        .attr('y2', function (link) { return link.target.y });
}
