from Queue import Queue

from pyposey.assembly_graph.Assembly_Graph import Assembly_Graph
from pyposey.assembly_graph.Part_Library import Part_Library

from Graph import Graph
from Graph_Node import Graph_Node
import Graph_Matcher as GM

from pyposey.assembly_graph.Hub import Hub
from pyposey.assembly_graph.Strut import Strut

import XMLParser as XP
import os

class Molecules:
  def __init__ (self, event_queue, isomorphism_list ):
    self.isomorphism_list = isomorphism_list
    self.original_isomorphism_list = isomorphism_list[:]
    self.part_library = Part_Library( hub_class=Hub,
                                     strut_class=Strut )
    self.assembly_graph = Assembly_Graph( event_queue=event_queue,
                                              part_library=self.part_library )
    self.iso_graph = Graph()
    self.node_dict = {}

    self.assembly_graph.start()

    self.assembly_graph.observers.append( self.update_isomorphisms )

  def filter_isomorphisms( self, large ):
    self.count += 1
    if self.count % 1 == 0:
      print "molecule: %d" % self.count
    gm = GM.Graph_Matcher(large[1], self.iso_graph)
    iso = gm.has_isomorphism()
    return iso

  def update_isomorphisms( self, event ):

    if event["type"] == "create":
      print "create"
      gn = Graph_Node(self.part_library[event["hub"]].label)
      self.node_dict[event["hub"]] = gn
      self.iso_graph.add_node(gn)

    elif event["type"] == "destroy":
      print "destroy"
      gn = self.node_dict[event["hub"]]
      self.iso_graph.remove_node(gn)
      del self.node_dict[event["hub"]]
      self.isomorphism_list = self.original_isomorphism_list[:]

    elif event["type"] == "connect":
      print "connect"
      gn1 = self.node_dict[event["hub"]]
      strut = self.assembly_graph.parts[event["strut"]]
      hubs = strut.get_connected()
      flag = 0
      for hub in hubs:
        if hub.address != event["hub"]:
          gn2 = self.node_dict[hub.address]
          self.iso_graph.add_edge(gn1, gn2)
          flag = 1
          break
      if not flag:
        return

    elif event["type"] == "disconnect":
      print "disconnect"
      gn1 = self.node_dict[event["hub"]]
      strut = self.assembly_graph.parts[event["strut"]]
      hubs = strut.get_connected()
      flag = 0
      for hub in hubs:
        if hub.address != event["hub"]:
          gn2 = self.node_dict[hub.address]
          self.iso_graph.remove_edge(gn1, gn2)
          self.isomorphism_list = self.original_isomorphism_list[:]
          flag = 1
          break
      if not flag:
        return

    elif event["type"] == "configure":
      pass

    from time import clock
    t = clock()
    self.count = 0
    self.isomorphism_list = filter(self.filter_isomorphisms, self.isomorphism_list)
    print "runtime: %f" % (clock() - t)

    print "possible molecules: %d\n" % len(self.isomorphism_list)
#    print "\n\nPossible molecule:"
#    for el in self.isomorphism_list:
#      print el[0]
#      for (u,n) in el[1].node_dict.iteritems():
#        ix = el[1].index_dict[u]
#        print "%d : %s" % (ix, n.label)
#      print el[1].adj_matrix
#      print "\n"

def import_molecule (name):
  print "Importing %s..." % name,
  m = XP.parse_file("./molecule_data/" + name)
  print "done."
  return m

if __name__ == "__main__":
    assembly_queue = Queue()

    data_files = os.listdir ("./molecule_data")
    
#   f = lambda n : XP.parse_file("./molecule_data/" + n)
    molecule_list = map (import_molecule, data_files)

    app = Molecules( assembly_queue, molecule_list )

    assembly_queue.put({"type": "create",
                        "hub": (88,1)})

    assembly_queue.put({"type": "create",
                        "hub": (42,3)})

    assembly_queue.put({ "type":    "connect",
                         "hub":     ( 42, 3 ),
                         "socket":  0,
                         "strut":   ( 3, 17 ),
                         "ball":    0 })

    assembly_queue.put({ "type":    "connect",
                         "hub":     ( 88, 1 ),
                         "socket":  0,
                         "strut":   ( 3, 17 ),
                         "ball":    1 })

    assembly_queue.put({"type": "create",
                        "hub": (42,5)})

    assembly_queue.put({ "type":    "connect",
                         "hub":     ( 42, 5 ),
                         "socket":  0,
                         "strut":   ( 3, 18 ),
                         "ball":    0 })

    assembly_queue.put({ "type":    "connect",
                         "hub":     ( 88, 1 ),
                         "socket":  1,
                         "strut":   ( 3, 18 ),
                         "ball":    1 })

    assembly_queue.put({ "type":    "disconnect",
                         "hub":     ( 42, 3 ),
                         "socket":  0,
                         "strut":   ( 3, 17 ),
                         "ball":    0 })

    assembly_queue.put({"type": "destroy",
                        "hub": (42,3)})

