# a graph is a graphnode list
# note graphs can be directed

from Graph_Node import Graph_Node
from Numeric import *

class Graph:
  adj_matrix = None
  index_dict = None  # nodeid |-> ix
  node_dict = None   # nodeid |-> node

  def __init__ (self, nodelist=[]):
    dim = len(nodelist)
    self.adj_matrix = zeros((dim,dim), Int8)
    self.index_dict = {}
    self.node_dict = {}
    i = 0
    for eli in nodelist:
      self.index_dict[eli.unique] = i
      j = 0
      for elj in nodelist:
        if elj in eli.neighbors:
          self.adj_matrix[i,j] = 1
        ++j
      ++i

  def add_node (self, node):
    oldshape = self.adj_matrix.shape
    oldrows = oldshape[0]
    oldcols = oldshape[1]
    newrow = zeros((1,oldcols))
    newcol = zeros((oldrows+1,1))
    self.adj_matrix = concatenate( (self.adj_matrix,newrow), 0)
    self.adj_matrix = concatenate( (self.adj_matrix,newcol), 1)

    #assumes square matrix; should always be true
    index = oldrows
    self.index_dict[node.unique] = index
    self.node_dict[node.unique] = node

    for el in node.neighbors:
      self.adj_matrix[index, self.index_dict[el.unique]] = 1
      self.adj_matrix[self.index_dict[el.unique], index] = 1

    node.add_to_graph(self)
    

  def remove_node (self, node):
    index = self.index_dict[node.unique]

    oldshape = self.adj_matrix.shape
    oldrows = oldshape[0]
    oldcols = oldshape[1]

    fstpart = self.adj_matrix[0:index,:]
    sndpart = self.adj_matrix[index+1:oldcols,:]
    self.adj_matrix = concatenate((fstpart,sndpart),0)

    fstpart = self.adj_matrix[:,0:index]
    sndpart = self.adj_matrix[:,index+1:oldrows]
    self.adj_matrix = concatenate((fstpart,sndpart),1)

    node.remove_from_graph(self)

    del self.index_dict[node.unique]
    del self.node_dict[node.unique]

    for node,ix in self.index_dict.iteritems():
      if ix > index:
        self.index_dict[node] = ix - 1


  def add_edge (self, node1, node2):
    if self.has_edge(node1, node2):
      return
    print "adding %d<->%d edge" % (node1.unique, node2.unique)
    index1 = self.index_dict[node1.unique]
    index2 = self.index_dict[node2.unique]
    #directed graph?
    self.adj_matrix[index1,index2] = 1
    self.adj_matrix[index2,index1] = 1

    node1.add_edge(node2)
    node2.add_edge(node1)

  def remove_edge (self, node1, node2):
    index1 = self.index_dict[node1.unique]
    index2 = self.index_dict[node2.unique]
    #directed graph?
    self.adj_matrix[index1,index2] = 0
    self.adj_matrix[index2,index1] = 0

    node1.remove_edge(node2)
    node2.remove_edge(node1)

  def set_neighbors (self, node, neighbors):
    index = self.index_dict[node.unique]
    shape = self.adj_matrix.shape
    rows = shape[0]
    cols = shape[1]

    for i in range(0,rows):
      self.adj_matrix[i, index]
    for j in range(0,cols):
      self.adj_matrix[index,j]

    for el in neighbors:
      self.adj_matrix[index,index_dict[node.unique]] = 1
      self.adj_matrix[index_dict[node.unique],index] = 1

    for el in node.neighbors:
      el.remove_edge(node)
    node.set_neighbors(neighbors)
    for el in neighbors:
      el.add_edge(node)

  def has_edge (self, node1, node2):
    return self.adj_matrix[self.index_dict[node1.unique],self.index_dict[node2.unique]]
