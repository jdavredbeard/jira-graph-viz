// Copyright 2019 Elsevier Inc.

// This file is part of jira-graph-viz.

// jira-graph-viz is free software: you can redistribute it and/or modify
// it under the terms of the GNU General Public License as published by
// the Free Software Foundation, either version 3 of the License, or
// (at your option) any later version.

// jira-graph-viz is distributed in the hope that it will be useful,
// but WITHOUT ANY WARRANTY; without even the implied warranty of
// MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
// GNU General Public License for more details.

// You should have received a copy of the GNU General Public License
// along with jira-graph-viz.  If not, see <https://www.gnu.org/licenses/>

var svg = d3.select('body').append('svg').attr('width', WIDTH).attr('height', HEIGHT),
    nodeLink = svg.append('g').attr('class', 'nodeLinks').selectAll('line'),
    node = svg.append('g').attr('class', 'nodes').selectAll('circle'),
    keyLink = svg.append('g').attr('class', 'keyLinks').selectAll('a');

var div = d3.select('body').append('div')
    .attr('class', 'tooltip')

var linkForce = d3.forceLink()
    .id(function (link) { return link.key })

var simulation = d3.forceSimulation()
    .force('link', linkForce)
    .force('charge', d3.forceManyBody().strength(FORCE_MANY_BODY_STRENGTH))
    .force('center', d3.forceCenter(X_CENTER, Y_CENTER))
    .force('x', d3.forceX())
    .force('y', d3.forceY())
    .force('collision', d3.forceCollide().radius(FORCE_COLLIDE_RADIUS))
    .force('radial', d3.forceRadial(getRadialForceRadiusFromTicketStatus, X_CENTER, Y_CENTER).strength(FORCE_RADIAL_STRENGTH))
    .on('tick', ticked);

var dragDrop = d3.drag().on('start', function (node) {
    node.fx = node.x
    node.fy = node.y
}).on('drag', function (node) {
    simulation.alphaTarget(DRAG_ALPHA_TARGET).restart()
    node.fx = d3.event.x
    node.fy = d3.event.y
}).on('end', function (node) {
    if (!d3.event.active) {
        simulation.alphaTarget(DROP_ALPHA_TARGET)
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
        .attr('stroke-width', NODE_BORDER_WIDTH)
        .merge(node)
        .call(dragDrop)
        .on('mouseover', handleMouseOver)
        .on('mouseout', handleMouseOut)

    nodeLink = nodeLink.data([...links], d => d.source + ' ' + d.target);
    nodeLink.exit().remove();
    nodeLink = nodeLink.enter()
        .append('line')
        .attr('stroke-width', LINK_LINE_WIDTH)
        .attr('stroke', getLineColorFromLinkType)
        .attr('stroke-dasharray', LINK_LINE_DASH_ARRAY)
        .attr('opacity', LINK_LINE_OPACITY)
        .merge(nodeLink);

    keyLink = keyLink.data([...dataset], d => d.key);
    keyLink.exit().remove();
    keyLink = keyLink.enter()
        .append('a')
        .attr('href', function(d) { return JIRA_BASE_URL + d.key})
        .attr('target', '_blank')
        .append('text')
        .text(node => node.key)
        .attr('font-family', 'Helvetica, sans-serif')
        .attr('font-size', KEY_TEXT_FONT_SIZE)
        .attr('font-weight', 'bold')
        .attr('dx', getKeyTextDxOffsetFromKeyLength)
        .attr('dy', getKeyTextDyOffsetFromTicketType)
        .style('cursor', 'pointer')
        .merge(keyLink);

    nestedKeyText = svg.selectAll('text');

    simulation.nodes([...dataset])
    simulation.force('link').links([...links]);
    simulation.alpha(RESTART_ALPHA).restart();
}

function getKeyTextDxOffsetFromKeyLength(d) {
    return -(d.key.length * KEY_TEXT_DX_OFFSET_MULTIPLIER)
}

function getKeyTextDyOffsetFromTicketType(d) {
    if (d.issuetype in NODERADIUS) return NODERADIUS[d.issuetype] + KEY_TEXT_DY_OFFSET;
    return KEY_TEXT_DY_OFFSET_DEFAULT;

}

function getRadiusFromTicketType(d) {
    if (d.issuetype in NODERADIUS) return NODERADIUS[d.issuetype];
    return NODE_RADIUS_DEFAULT;

}

function getRadialForceRadiusFromTicketStatus(d) {
    if (d.status in RADIALFORCERADIUS) return RADIALFORCERADIUS[d.status];
    return RADIAL_FORCE_RADIUS_DEFAULT;
}

function handleMouseOver(d, i) {
    d3.select(this).attr('fill', 'orange');
    div.transition()
        .duration(MOUSE_OVER_DURATION)
        .style('opacity', MOUSE_OVER_OPACITY);
    div .html('<b>Summary: </b>' + d.summary + '<br/>'  +
        '<b>Priority: </b>' + d.priority + '<br/>' +
        '<b>Assignee: </b>' + d.assignee + '<br/>' +
        '<b>Issuetype: </b>' + d.issuetype + '<br/>' +
        '<b>Status: </b>' + d.status)
        .style('left', (d3.event.pageX) + 'px')
        .style('top', (d3.event.pageY - TOOL_TIP_Y_OFFSET) + 'px');
}

function handleMouseOut(d, i) {
    d3.select(this).attr('fill', getNodeColorFromStatus);
    div.transition()
        .duration(MOUSE_OUT_DURATION)
        .style('opacity', MOUSE_OUT_OPACITY);
}

function getStrokeColor(d) {
    if (querySet.has(d.key)) return 'black';
    return getNodeColorFromStatus;
}

function getNodeColorFromStatus(node) {
    if (node.status in STATUSCOLORS) return STATUSCOLORS[node.status];
    return 'black';
}

function getLineColorFromLinkType(link) {
    if (link.type in LINKCOLORS) return LINKCOLORS[link.type];
    return 'black';
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
