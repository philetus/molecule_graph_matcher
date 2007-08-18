import random as R
from Numeric import *
import Graph_Matcher as GM
import Graph_Node as GN
import Graph as G

big_lo = 5
big_hi = 25
small_lo = 2

def gen_iso ():
  big = R.randint(big_lo,big_hi)
  small = R.randint(small_lo,big)
  nodes = []
  i = 0
  #print "0"
  while len(nodes) < small:
    node = R.randint(0,big - 1)
    if node not in nodes:
      nodes.append(node)
  
  B = G.Graph()
  S = G.Graph()
  bdict = {}
  sdict = {}

  for i in range(0,big):
    gn = GN.Graph_Node("a")
    bdict[i] = gn
    B.add_node(gn)
  for i in range(0,big):
    for j in range(0,big):
      if i != j and R.randint(0,7) == 0:
        B.add_edge(bdict[i],bdict[j])

  print ("-")

  for i in range(0,small):
    gn = GN.Graph_Node("a")
    sdict[i] = gn
    S.add_node(gn)
  for i in range(0,small):
    for j in range(0,small):
      if B.has_edge(bdict[nodes[i]],bdict[nodes[j]]):
        if R.randint(0,1):
          S.add_edge(sdict[i],sdict[j])

  goodM = zeros((small,big))
  for i in range(0,small):
    print sdict[i].unique
    goodM[i,nodes[i]] = 1
  print " "
  for j in range(0,big):
    print bdict[j].unique
  print "good M:"
  print goodM

  return (B,S,nodes)
  
while 1:
  (B,S,nodes) = gen_iso ()
  #print "node map:"
  #print nodes
  #print "B:"
  #print B.adj_matrix
  #print "S:"
  #print S.adj_matrix
  #print "\n\n"
  gm = GM.Graph_Matcher(B,S)
  if gm.has_isomorphism():
    print "."
  else:
    print "!"
