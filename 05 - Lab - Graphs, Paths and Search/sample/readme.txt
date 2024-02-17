Created for COS30002 AI for Games by Clinton Woodward cwoodward@swin.edu.au

Graph Searching
===============

Objective: To understand Depth First Search (DFS), Breadth First Search (BFS), Dijkstra’s and A* Search algorithms applied to a simple “box” based world.


Quick Start:
------------
Download code for this lab from blackboard. Extract to your favourite work location. The file to run is main.py. You will need to specify a map file to load. Something like:
  C:>python main.py map1.txt

Keys:
-----

1: “clear” (white)
2: “mud” (grey-brownish)
3: “water” (blue)
4: “wall” (black)
5: “start”
6: “target”

SPACE: force a replan (execute search)
N and M: cycle (back or forward) through the search methods and replan.
UP and DOWN: Increase or decrease the search step limit by one.
0: Remove the search step limit. (A full search will be performed.)

E: toggle edges on/off for the current navigation graph (thin blue lines)
L: toggle box (node) index values on/off (useful for understanding search and path details).
C: toggle box “centre” markers on/off
T: toggle tree on/off for the current search if available
P: toggle path on/off for the current search if there is a successful route.



Maps
----

There are two simple maps to start with named map1.txt and map2.txt. You can create your own later if you wish.

The worlds boxes can be changed with a combination of selecting the box “kind” (show in the top left text) and then left-clicking on to a box. There are currently four different box kinds:
  1: “clear” (white)
  2: “mud” (grey-brownish)
  3: “water” (blue)
  4: “wall” (black)

Walls are not included (have no edges) in the navigation graph.

For each search a start (“S”) and target (“T”) box is needed. To change the location of either, first set the kind value, and click on to a box.
  5: “start”
  6: “target”

You can allocate start or target to wall box that has no edges, however this will stop any search from being successful!

Pressing the SPACE key will perform a search using the current map and search mode, however most changes to the world force a new search to be done immediately.
  "SPACE": performace full search (if not already done)

There are currently four different search modes, which can be cycled through using the N and M keys (backwards and forwards respectively).
  "N": previous search mode
  "M": next search mode
The search modes are:
  “BFS” for Best First search algorithm
  “DFS” for Depth First search algorithm “Dijkstra” for Dijkstra’s lowest-cost-so-far search algorithm
  “A*” (written as “AStar”) for the lowest cost-so-far + lowest-estimated-cost algorithm

Search “depth” (the number of search steps taken) can be limited and changed using the UP and DOWN arrow keys. The limit can be removed using the “0” key.
  "UP": increase search step depth limit
  "DOWN": decrease search step depth
  "0": remove search step limit

