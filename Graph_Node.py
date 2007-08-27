#from Graph import Graph

uniquifier = 0

class Graph_Node:

  label = None
  neighbors = None
  unique = 0
  graph = None
  degree = 0

  def __init__(self, label, neighbors=None):
    self.label = label
    if neighbors is None:
      self.neighbors = []
    else:
      self.neighbors = neighbors
    self.degree = len(self.neighbors)

    global uniquifier
    self.unique = uniquifier
    uniquifier += 1

  # DO NOT USE BELOW FUNCTIONS
  # instead use corresponding graph functions on this node
  def add_to_graph (self, g):
    self.graph = g

  def remove_from_graph (self, g):
    self.graph = None

  def add_edge (self, neighbor):
    self.neighbors.append(neighbor)
    self.degree += 1

  def remove_edge (self, neighbor):
    filter((lambda x : x is not neighbor), self.neighbors)
    self.degree -= 1

  def set_neighbors(self, neighbors):
    self.neighbors = neighbors
    degree = len(neighbors)
