import Graph as G
import Graph_Node as GN

a = GN.Graph_Node ("a")
b = GN.Graph_Node ("b")
c = GN.Graph_Node ("c")
d = GN.Graph_Node ("d")
e = GN.Graph_Node ("e")

g = G.Graph()
print "Empty graph"
print g.adj_matrix

g.add_node(a)
print "Singleton graph"
print g.adj_matrix

g.add_node(b)
g.add_node(c)
g.add_node(d)
print "4 node graph"
print g.adj_matrix

g.add_edge(a,b)
print "1 edge"
print g.adj_matrix

g.add_edge(b,c)
g.add_edge(c,d)
g.add_edge(d,a)
print "4 edges"
print g.adj_matrix

g.remove_edge(a,b)
print "a,b edge removed"
print g.adj_matrix

g.remove_node(b)
print "b node removed"
print g.adj_matrix

g.add_edge(a,c)
print "a,c edge added"
print g.adj_matrix

g.add_node(e)
print "added e node"
print g.adj_matrix

g.add_edge(e,c)
print "added e,c edge"
print g.adj_matrix
