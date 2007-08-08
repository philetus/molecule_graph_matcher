from Graph_Node import Graph_Node
from Graph import Graph
from Isomorphism import Isomorphism
from Numeric import *

class Graph_Matcher:
  isomorphisms = None


  def __init__ (self, large, small):
    self.large = large
    self.small = small


  #from Ullman, 1976
  def find_isomorphisms ():
    #initialize some things
    A = self.small.adj_matrix
    B = self.large.adj_matrix
    M0 = zeros((self.small.shape[0],self.large.shape[0]))
    for (nodei,indexi) in self.small.iteritems():
      for (nodej,indexj) in self.large.iteritems():
        if nodei.label == nodej.label and nodei.degree < nodej.degree:
          M0[i,j] = 1
    #enumerate allowable permutations
    isomorphisms = []
    perm = first_permutation(M0)
    while next_permuatations(M0, perm, 0, self.small.shape[0]):
      M = mat_from_perm(perm)
      if is_isomorphism(A,B,M):
        self.isomorphisms.append(M) #copy matrix to list


  def has_isomorphism ()
    #initialize some things
    A = self.small.adj_matrix
    B = self.large.adj_matrix
    M0 = zeros((self.small.shape[0],self.large.shape[0]))
    for (nodei,indexi) in self.small.iteritems():
      for (nodej,indexj) in self.large.iteritems():
        if nodei.label == nodej.label and nodei.degree < nodej.degree:
          M0[i,j] = 1
    return next_permuatations(M0, perm, 0, self.small.shape[0])


  def mat_from_perm(M0,perm):
    M = zeros((M0.shape[0],M0.shape[1]))
    for i in range(0,perm.shape[0]):
      M[i,perm[i]] = 1
    return M


  def first_permutation(M0):
    p = zeros((M0.shape[0]))
    p = p - 1
    return p


  def next_permutation(M0,perm,depth,max_depth):
    if depth >= max_depth:
      return perm
    if find_this_row(M0,perm,depth):
      for i in range(depth+1,max_depth):
        perm[i] = -1
      if next_permutation(M0,perm,depth+1,max_depth):
        return true
      else:
        return false
    else:
      return false


  def allowable_position(M0,perm,depth,i):
    if M0[depth,i] == 0:
      return false
    for j in range(0,depth):
      if(M0[j,perm[j]]) == 1:
        return false
    return true


  def find_this_row(M0,perm,depth):
    for i in range(perm[depth] + 1, M0.shape[1]):
      if allowable_position(M0,perm,depth,i):
        perm[depth] = i
        return true
    return false


  def is_isomorphism (A,B,M):
    C = matrixmultiply(M,transpose(matrixmultiply(M,B)))
    for (i,j) in A.shape:
      if A[i,j] == 1 and C[i,j] == 0:
        return false
    return true
