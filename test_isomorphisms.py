import random as R
from Numeric import *
import Graph_Matcher as GM
import Graph_Node as GN
import Graph as G

big_lo = 3
big_hi = 7
small_lo = 3

def gen_iso ():
  big = R.randint(big_lo,big_hi)
  small = R.randint(small_lo,big)
  nodes = []
  i = 0
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

  for i in range(0,small):
    gn = GN.Graph_Node("a")
    sdict[i] = gn
    S.add_node(gn)
  for i in range(0,small):
    for j in range(0,small):
      if B.has_edge(bdict[nodes[i]],bdict[nodes[j]]):
        if R.randint(0,1):
          S.add_edge(sdict[i],sdict[j])


  return (B,S,nodes)

def foo ():
  for x in range(0,1000):
    (B,S,nodes) = gen_iso ()
#    print "genning iso"
    gm = GM.Graph_Matcher(B,S)
#    print "testing"
    if gm.has_isomorphism():
      print "."
    else:
      print "!"

import profile
profile.run("foo()")
