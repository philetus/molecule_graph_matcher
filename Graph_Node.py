#from Graph import Graph

uniquifier = 0

class Graph_Node:

  label = None
  neighbors = None
  unique = 0
  graph = None
  degree = 0

  def __init__(self, label, neighbors=[]):
    self.label = label
    self.neighbors = neighbors
    self.degree = len(neighbors)

    global uniquifier
    self.unique = uniquifier
    uniquifier += 1

  # DO NOT USE BELOW FUNCTIONS
  # instead use corresponding graph functions on this node
  def add_to_graph (self, g):
    self.graph = g

  def remove_from_graph (self, g):
    self.graph = None

  def add_edge (neighbor):
    self.neighbors.append(neighbor)
    ++ self.degree

  def remove_edge (neighbor):
    self.neighbors.filter((lambda x : x is not neighbor), self.neighbors)
    -- self.degree

  def set_neighbors(self, neighbors):
    self.neighbors = neighbors
    degree = len(neighbors)
