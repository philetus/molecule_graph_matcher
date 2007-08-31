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

import Tkinter

class Molecules:
  def __init__ (self, event_queue, isomorphism_list, set_gui_list):
    self.isomorphism_list = isomorphism_list
    self.original_isomorphism_list = isomorphism_list[:]
    self.part_library = Part_Library( hub_class=Hub,
                                     strut_class=Strut )
    self.assembly_graph = Assembly_Graph( event_queue=event_queue,
                                              part_library=self.part_library )
    self.iso_graph = Graph()
    self.node_dict = {}
    self.socket_dict = {}

    self.set_gui_list = set_gui_list

    print "Initial possible molecules (%d):" % len(self.isomorphism_list)
    self.isomorphism_list.sort(key=self.molecule_key)
    self.set_gui_list(self.isomorphism_list)
    for el in self.isomorphism_list:
      print "%s,"% el[0],
    gm = GM.Graph_Matcher(self.isomorphism_list[0][1], self.iso_graph)
    print ""
    if gm.is_isomorphism():
      print "You have %s." % self.isomorphism_list[0][0]
    print "\n"

    self.assembly_graph.start()

    self.assembly_graph.observers.append( self.update_isomorphisms )

  def molecule_key (self, m):
    return m[1].adj_matrix.shape[0]

  def filter_isomorphisms( self, large ):
    #self.count += 1
    #if self.count % 1 == 0:
    #  print "molecule: %d" % self.count
    #for (label, count) in self.iso_graph.label_count.iteritems():
    #  if not large[1].label_count.has_key(label):
    #    return 0
    #  if large[1].label_count[label] < self.iso_graph.label_count[label]:
    #    return 0
    gm = GM.Graph_Matcher(large[1], self.iso_graph)
    iso = gm.has_isomorphism()
    return iso

  def update_isomorphisms( self, event ):
    raw_input (" ")
    print "---------------------------------------"

    if event["type"] == "create":
      gn = Graph_Node(self.part_library[event["hub"]].label)
      print "Received create event: %s(%d)." % (gn.label, gn.unique)
      self.node_dict[event["hub"]] = gn
      self.iso_graph.add_node(gn)

    elif event["type"] == "destroy":
      gn = self.node_dict[event["hub"]]
      print "Received destroy event: %s(%d)" % (gn.label, gn.unique)
      self.iso_graph.remove_node(gn)
      del self.node_dict[event["hub"]]
      self.isomorphism_list = self.original_isomorphism_list[:]

    elif event["type"] == "connect":
      gn1 = self.node_dict[event["hub"]]
      strut = self.assembly_graph.parts[event["strut"]]
      self.socket_dict[(event["hub"],event["socket"])] = strut
      hubs = strut.get_connected()
      flag = 0
      for hub in hubs:
        if hub.address != event["hub"]:
          gn2 = self.node_dict[hub.address]
          print "Received connect event: %s(%d) <--> %s(%d)" % (gn1.label,gn1.unique,gn2.label,gn2.unique)
          self.iso_graph.add_edge(gn1, gn2)
          flag = 1
          break
      if not flag:
        print "Receive effectless connect event:  %s(%d)" % (gn1.label,gn1.unique)
        return

    elif event["type"] == "disconnect":
      gn1 = self.node_dict[event["hub"]]
      strut = self.socket_dict[(event["hub"],event["socket"])]
      hubs = strut.get_connected()
      flag = 0
      for hub in hubs:
        if hub.address != event["hub"]:
          gn2 = self.node_dict[hub.address]
          print "Received disconnect event: %s(%d) <-/-> %s(%d)" % (gn1.label,gn1.unique,gn2.label,gn2.unique)
          self.iso_graph.remove_edge(gn1, gn2)
          self.isomorphism_list = self.original_isomorphism_list[:]
          flag = 1
          break
      if not flag:
        print "Receive effectless disconnect event:  %s(%d)" % (gn1.label,gn1.unique)
        return

    elif event["type"] == "configure":
      pass

    self.isomorphism_list = filter(self.filter_isomorphisms, self.isomorphism_list)

#    print "possible molecules: %d\n" % len(self.isomorphism_list)
#    print "Molecule graph is:"
#    for (u,n) in self.iso_graph.node_dict.iteritems():
#      ix = self.iso_graph.index_dict[u]
#      print "%d : %s" % (ix, n.label)
#    print self.iso_graph.adj_matrix
#    print "\n"

    print "Possible molecules (%d):" % len(self.isomorphism_list)
    self.isomorphism_list.sort(key=self.molecule_key)
    self.set_gui_list(self.isomorphism_list)
    for el in self.isomorphism_list:
      print "%s," % el[0],
    gm = GM.Graph_Matcher(self.isomorphism_list[0][1], self.iso_graph)
    print ""
    if gm.is_isomorphism():
      print "You have %s." % self.isomorphism_list[0][0]
#      for (u,n) in el[1].node_dict.iteritems():
#        ix = el[1].index_dict[u]
#        print "%d : %s" % (ix, n.label)
#      print el[1].adj_matrix
#      print "\n"
    print "\n"

def import_molecule (name):
  #print "Importing %s..." % name,
  m = XP.parse_file("./molecule_data/" + name)
  #print "done."
  return m

#XXX __init__ magic?
def start(set_listbox):
    assembly_queue = Queue()

    data_files = os.listdir ("./molecule_data")
    
    molecule_list = map (import_molecule, data_files, )
    print ""

    app = Molecules( assembly_queue, molecule_list, set_listbox )

    assembly_queue.put({"type": "create",
                        "hub": (88,1)})

    assembly_queue.put({"type": "create",
                        "hub": (42,3)})

    assembly_queue.put({"type": "create",
                        "hub": (42,4)})

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

    assembly_queue.put({ "type":    "connect",
                         "hub":     ( 42, 4 ),
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
                         "socket":  0})

    assembly_queue.put({"type": "destroy",
                        "hub": (42,3)})
