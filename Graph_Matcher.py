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
  def find_isomorphisms (self):
    #initialize some things
    A = self.small.adj_matrix
    B = self.large.adj_matrix
    M0 = zeros((A.shape[0],B.shape[0]))
    i = 0
    keyf = lambda x : x[1]
    for (uniquei,ixi) in sorted([x for x in self.small.index_dict.iteritems()], key = keyf):
      j = 0
      for (uniquej,ixj) in sorted([x for x in self.large.index_dict.iteritems()], key = keyf):
        nodei = self.small.node_dict[uniquei]
        nodej = self.large.node_dict[uniquej]
        if nodei.label == nodej.label and nodei.degree <= nodej.degree:
          M0[i,j] = 1
        j += 1
      i += 1

    #enumerate allowable permutations
    isomorphisms = []
    perm = self.first_permutation(M0)
    while self.next_permutation(M0, perm, 0, A.shape[0]):
      M = self.mat_from_perm(perm)
      if self.is_isomorphism(A,B,M):
        self.isomorphisms.append(M) #copy matrix to list


  def has_isomorphism (self):
    #initialize some things
    A = self.small.adj_matrix
    B = self.large.adj_matrix
    M0 = zeros((A.shape[0],B.shape[0]))
    i = 0
    keyf = lambda x : x[1]
#    print "making M0"
    for (uniquei,ixi) in sorted([x for x in self.small.index_dict.iteritems()], key = keyf):
      j = 0
      for (uniquej,ixj) in sorted([x for x in self.large.index_dict.iteritems()], key = keyf):
        nodei = self.small.node_dict[uniquei]
        nodej = self.large.node_dict[uniquej]
        if nodei.label == nodej.label and nodei.degree <= nodej.degree:
          M0[i,j] = 1
        j += 1
      i += 1
    print "M0 is "
    print M0
#    print "done"
    perm = self.first_permutation(M0)
#    print "enumming perms"
    while self.next_permutation(M0, perm, 0, A.shape[0]):
#      print "  finding perm"
      M = self.mat_from_perm (M0,perm)
#      print "  perm found"
      if self.is_isomorphism(A,B,M):
        return 1
    return 0


  def mat_from_perm(self, M0, perm):
    M = zeros((M0.shape[0],M0.shape[1]))
    for i in range(0,perm.shape[0]):
      M[i,perm[i]] = 1
    return M


  def first_permutation(self, M0):
    p = zeros((M0.shape[0]))
    p -= 1
    return p


  def next_permutation(self,M0,perm,depth,max_depth):
    if depth == max_depth - 1:
      return self.find_this_row(M0,perm,depth)
    if perm[depth] != -1:
      if  self.next_permutation(M0,perm,depth+1,max_depth):
        return 1
    while self.find_this_row(M0,perm,depth):
      i = depth + 1
      while i < max_depth:
        perm[i] = -1
        i += 1
      if  self.next_permutation(M0,perm,depth+1,max_depth):
        return 1
    return 0


  def find_this_row(self,M0,perm,depth):
    i = perm[depth] + 1
    max = M0.shape[1]
    while i < max:
      if self.allowable_position(M0,perm,depth,i):
        perm[depth] = i
        return 1
      i += 1
    return 0


  def allowable_position(self,M0,perm,depth,i):
    if M0[depth,i] == 0:
      return 0
    j = 0
    while j < depth:
      if perm[j] == i:
        return 0
      j += 1
    return 1


  def is_isomorphism (self,A,B,M):
    C = matrixmultiply(M,transpose(matrixmultiply(M,B)))
    for i in range(0,A.shape[0]):
      for j in range(0,A.shape[1]):
        if A[i,j] == 1 and C[i,j] == 0:
          return 0 
    return 1
