# WireWorld
This program is designed to run the cellular automata WireWorld. The class 
'World' is designed to be flexible enough to run different kinds of 
cellular automata. 

I have chosen to represent the state of the 'world' by a dictionary with 
coordinates as keys and states as the values. This choice is particularly 
suitable to the wireworld cellular automata because it has a stable 0 
state. By this, I mean that a cell with state 0 will remain in state 0. 
It is therefore not necessary to update these cells, the important cells 
are all non-zero. By ommiting the coordinates with state 0 from the 
dictionary, the program becomes much more scalable for sparse worlds spread 
over a large area. For example, a wire running along the perimeter of an 
otherwise empty square of size n will run at, and use O(n) space rather 
than O(n^2).

A weaker version of this 0 stability property holds for other cellular 
automata such as John Conway's game of life or Langtons ant.  In these, a 
cell in state 0 surrounded by cells in state 0 will remain in state 0. For 
such cellular automata, it is only necessary to update non-zero cells and 
cells immediately adjacent to non-zero cells. In such cases, world.mode is 
set to semistable and the getneighbours method will create the adjacent 0 
cells with the setdefault method.
