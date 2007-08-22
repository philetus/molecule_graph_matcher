import XMLParser as XP

g = XP.parse_file("molecule_data/CID_962.xml");

for (u,n) in g.node_dict.iteritems():
  print "(%s,%d)" % (n.label,g.index_dict[u])

print g.adj_matrix
