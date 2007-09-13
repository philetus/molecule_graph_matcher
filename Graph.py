# a graph is stored as an adjacency matrix, but manipulated by creating
# and working with Graph_Nodes to have a clean interface.

from Graph_Node import Graph_Node
from Numeric import *

class Graph:
  # adacency matrix
  adj_matrix = None
  # map from node unique ids (ints) to adj matrix indices
  index_dict = None 
  # map from node unique ids (ints) to node objects
  node_dict = None 
  # number of labels with this count XXX what is this used for?
  label_count = None

  # constructor creates a matrix, adds nodes to it
  def __init__ (self, nodelist=[]):
    dim = len(nodelist)
    self.adj_matrix = zeros((dim,dim), Int8)
    self.index_dict = {}
    self.node_dict = {}
    self.label_count = {}
    i = 0
    for eli in nodelist:
      self.index_dict[eli.unique] = i
      j = 0
      for elj in nodelist:
        if elj in eli.neighbors:
          self.adj_matrix[i,j] = 1
        ++j
      ++i

  # add a node to the graph
  def add_node (self, node):
    # expand the matrix by one row and one column
    # this is harder than it should be
    oldshape = self.adj_matrix.shape
    oldrows = oldshape[0]
    oldcols = oldshape[1]
    newrow = zeros((1,oldcols))
    newcol = zeros((oldrows+1,1))
    self.adj_matrix = concatenate( (self.adj_matrix,newrow), 0)
    self.adj_matrix = concatenate( (self.adj_matrix,newcol), 1)

    # add the new node to the index and node maps
    index = oldrows
    self.index_dict[node.unique] = index
    self.node_dict[node.unique] = node

    # add neighbors that the node has to the adj matrix
    for el in node.neighbors:
      self.adj_matrix[index, self.index_dict[el.unique]] = 1
      self.adj_matrix[self.index_dict[el.unique], index] = 1

    # tell the node we are adding it to the graph
    node.add_to_graph(self)

    # update the label count
    if self.label_count.has_key(node.label):
      self.label_count[node.label] += 1
    else:
      self.label_count[node.label] = 1
    
  # remove a node and all edges containing it
  def remove_node (self, node):
    # find out what adj matrix row and column we are removing
    index = self.index_dict[node.unique]

    # find matrix size
    oldshape = self.adj_matrix.shape
    oldrows = oldshape[0]
    oldcols = oldshape[1]

    # slice the matrix by rows, cutting out the removed row
    # and glue them back together
    fstpart = self.adj_matrix[0:index,:]
    sndpart = self.adj_matrix[index+1:oldcols,:]
    self.adj_matrix = concatenate((fstpart,sndpart),0)

    # by columns
    fstpart = self.adj_matrix[:,0:index]
    sndpart = self.adj_matrix[:,index+1:oldrows]
    self.adj_matrix = concatenate((fstpart,sndpart),1)

    # tell node we are removing it from the graph
    node.remove_from_graph(self)
    #decrement the count of this nodes label
    self.label_count[node.label] -= 1

    # remove node from the maps
    del self.index_dict[node.unique]
    del self.node_dict[node.unique]

    # decrement indices of nodes whose matrix indices are higher than this one's
    for node,ix in self.index_dict.iteritems():
      if ix > index:
        self.index_dict[node] = ix - 1


  # add an edge between nodes
  def add_edge (self, node1, node2):
    # if we already have it, return
    if self.has_edge(node1, node2):
      return
    #otherwise, find what indices we need to add a 1 at and do so
    index1 = self.index_dict[node1.unique]
    index2 = self.index_dict[node2.unique]
    self.adj_matrix[index1,index2] = 1
    self.adj_matrix[index2,index1] = 1

    # tell the nodes they have a new edge
    node1.add_edge(node2)
    node2.add_edge(node1)

  # remove an edfe
  def remove_edge (self, node1, node2):
    # find the indices of the two affected nodes
    index1 = self.index_dict[node1.unique]
    index2 = self.index_dict[node2.unique]
    
    #set the adjacency to 0
    self.adj_matrix[index1,index2] = 0
    self.adj_matrix[index2,index1] = 0

    # tell nodes they've lost an edge
    node1.remove_edge(node2)
    node2.remove_edge(node1)

  # set the neighbors for a node
  def set_neighbors (self, node, neighbors):
    # find the indices for this node
    index = self.index_dict[node.unique]
    # find the size of the matrix
    shape = self.adj_matrix.shape
    rows = shape[0]
    cols = shape[1]

    # zero out this node's old neighbors
    for i in range(0,rows):
      self.adj_matrix[i, index]
    for j in range(0,cols):
      self.adj_matrix[index,j]

    # set the new neighbors
    for el in neighbors:
      self.adj_matrix[index,index_dict[node.unique]] = 1
      self.adj_matrix[index_dict[node.unique],index] = 1

    # tell the old neighbors we are going away
    for el in node.neighbors:
      el.remove_edge(node)

    # tell the new neighbors hi
    node.set_neighbors(neighbors)
    for el in neighbors:
      el.add_edge(node)

  # does this edge exit
  def has_edge (self, node1, node2):
    return self.adj_matrix[self.index_dict[node1.unique],self.index_dict[node2.unique]]

  # tostring
  def __str__ (self):
    s = ""
    for (unique,ix) in sorted([x for x in self.index_dict.iteritems()], key = lambda x : x[1]):
       s += "%d:\"%s\"\n" % (ix, self.node_dict[unique].label)
    s += str(self.adj_matrix)
    return s
