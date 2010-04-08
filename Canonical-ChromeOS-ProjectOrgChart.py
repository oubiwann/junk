#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
{Matt \rZimmerman | CTO }(red)
    {Foundations | Robbie \rWilliamson} (blue)
        Scott James \rRemnant (red)
        Colin \rWatson (red)
        Loic \rMinier (blue)
        Matthias \rKlose (blue)
        Steve \rLangasek (blue)
    {Kernel | Pete \rGraner} (blue)
        Tim \rGardner (blue)
        Brad \rFigg (blue)
        Andy \rWhitcroft (blue)
        Hugh \rBlemings (blue)
            Jeremy \rKerr (blue)
    {Mobile | David \rMandala} (blue)
        Alexander \rSack (blue)
    {OEM | Chris \rKenyon} (red)
        Ram \rFish (red)
        Patrick \rMcGowan (red)
            Michael \rFrey (blue)
            Steve \rMagoun (dotted)
                Cody \rSomerville (blue)
    {Desktop | Rick \rSpencer} (blue)
        Bryce \rHarrington (blue)
        Luke \rYelavich (blue)
    {QA | Marjo \rMercado} (blue)
    Duncan \rMcGreggor (blue)
"""
import re
import sys

import pydot


styles = ["dotted"]


def getRank(spaces):
    length = len(spaces)
    if length == 0:
        return length
    else:
        return length / 4


def getParentRank(rank):
    parentRank = rank - 1
    if parentRank < 0:
        parentRank = None
    return parentRank


def parseNames():
    parser = re.compile(
        "(?P<rank>(\A\s+)?)(?P<name>.*)\s\((?P<color>.*)\)",
        re.DOTALL | re.MULTILINE)
    names = __doc__.strip().split("\n")
    data = []
    for line in names:
        match = parser.match(line)
        data.append({
            "rank": getRank(match.group("rank")),
            "name": match.group("name"),
            "color": match.group("color")})
    return data


def makeGraph():
    graph = pydot.Dot(graph_type="digraph")
    parents = {}
    for nodeData in parseNames():
        rank = nodeData["rank"]
        name = nodeData["name"]
        parents[rank] = name
        parent = parents.get(getParentRank(rank))
        color = nodeData["color"]
        kwargs = {
            "fontname": "Arial Black",
            "fontsize": "18"}
        if rank == 1:
            kwargs["shape"] = "record"
        else:
            kwargs["shape"] = "box"
        if color in styles:
            kwargs["style"] = "%s,setlinewidth(6)" % color
        else:
            kwargs["color"] = color
            kwargs["style"] = "filled,setlinewidth(4)"
            if color.lower() == "blue":
                kwargs["fillcolor"] = "lightblue"
            elif color.lower() == "red":
                kwargs["fillcolor"] = "lightcoral"
        node = pydot.Node(name, **kwargs)
        graph.add_node(node)
        if parent:
            edge = pydot.Edge(
                parent, node, style="setlinewidth(4)", arrowsize="2.0")
            graph.add_edge(edge)
    return graph


def generateChart(filename, format="png"):
    graph = makeGraph()
    result = graph.write(filename, prog="dot", format=format)
    if not result:
        raise Exception("There was a problem writing the file.")


if __name__ == "__main__":
    filename = sys.argv[1]
    generateChart(filename)
