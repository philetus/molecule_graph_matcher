#  Main molecule matching file.  It makes a list of graphs of molecule we have
#  a PubChem XML file for.  It also keeps track of a graph representing the
#  current state of the posey pieces.  Then it waits for assembly events.  On
#  an event, the posey graph is updated appropriately, and each the list of
#  possible molecules it matches is filtered by attempting to match the posey
#  graph against each possible molecule graph.

from Queue import Queue

from pyposey.assembly_graph.Assembly_Graph import Assembly_Graph

from pyposey.hardware_demon.Sensor_Demon import Sensor_Demon
from pyposey.hardware_demon.Assembly_Demon import Assembly_Demon

from pyposey.assembly_graph.Part_Library import Part_Library

from Graph import Graph
from Graph_Node import Graph_Node
import Graph_Matcher as GM

from pyposey.assembly_graph.Hub import Hub
from pyposey.assembly_graph.Strut import Strut

import XMLParser as XP
import os

import Tkinter

# most functionality (except for some initialization code) is held in this class.
class Molecules:

  # constructor sets up the class
  # It takes an event queue that will contain the posey assembly events, an
  # initial list of molecule graphs and two hooks into the gui, one to set the
  # list of elements displayed when a new posey graph is produced, and one to force
  # update of the currently displayed molecule.
  def __init__ (self, event_queue, isomorphism_list, set_gui_list, list_observer):
    # initialize various fields
    # list of possible molecules
    self.isomorphism_list = isomorphism_list
    # a copy of the original possible molecules for backtracking on
    # destroy or disconnect events
    self.original_isomorphism_list = isomorphism_list[:]
    # part data
    self.part_library = Part_Library( hub_class=Hub,
                                     strut_class=Strut )

    # assembly graph
    self.assembly_graph = Assembly_Graph( event_queue=event_queue,
                                              part_library=self.part_library )

    # posey graph
    self.iso_graph = Graph()
    # information on currently connected pieces to help update the graph
    self.node_dict = {}
    self.socket_dict = {}

    #setting gui hook
    self.set_gui_list = set_gui_list

    # print initial moledcules
    print "Initial possible molecules (%d):" % len(self.isomorphism_list)
    self.isomorphism_list.sort(key=self.molecule_key)
    self.set_gui_list(self.isomorphism_list)
    for el in self.isomorphism_list:
      print "%s,"% el[0],
    print ""
    print "\n"

    # start processing assembly events
    self.assembly_graph.start()

    # update molecule graph list on posey event
    self.assembly_graph.observers.append( self.update_isomorphisms )
    # update displayed molecule on posey event
    self.assembly_graph.observers.append( list_observer )

  # We sort molecules by size
  def molecule_key (self, m):
    return m[1].adj_matrix.shape[0]

  # Used with map: for each graph in our list, try to
  # match the posey graph to it.
  def map_isomorphisms( self, large ):
    gm = GM.Graph_Matcher(large[1], self.iso_graph)
    iso_map = gm.get_isomorphism()
    return (large[0], large[1], iso_map)

  # Used with filter to get rid of failed matches.
  def filter_isomorphisms( self, triple ):
    return triple[2] is not None

  # process assembly events; update graph; update list of molecules
  def update_isomorphisms( self, event ):

    #create event
    if event["type"] == "create":
      #find out what node this is
      gn = Graph_Node(self.part_library[event["hub"]].label)
      print "Received create event: %s(%d)." % (gn.label, gn.unique)
      # add it to dictionary of nodes in our graph
      self.node_dict[event["hub"]] = gn
      # add it to the graph
      self.iso_graph.add_node(gn)

    #destroy
    elif event["type"] == "destroy":
      # find out what node it is
      gn = self.node_dict[event["hub"]]
      print "Received destroy event: %s(%d)" % (gn.label, gn.unique)
      # remove node from graph
      self.iso_graph.remove_node(gn)
      # remove node from dictionary
      del self.node_dict[event["hub"]]
      # replace molecule list with original list
      # This requires some explanation.  Since we filter out unmatching graphs,
      # our list of matching molecules gets smaller monotonically.  When we
      # need to make our list larger on destroy or disconnect, we refilter the
      # whole list.
      self.isomorphism_list = self.original_isomorphism_list[:]

    # connect event
    elif event["type"] == "connect":
      # find what node we are connecting
      gn1 = self.node_dict[event["hub"]]
      # find what strut we are connecting to.
      strut = self.assembly_graph.parts[event["strut"]]
      # record this strut is in aour graph
      self.socket_dict[(event["hub"],event["socket"])] = strut
      # find the node at the other end of the strut and connect to it
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
        # no node at the other end of the strut
        print "Receive effectless connect event:  %s(%d)" % (gn1.label,gn1.unique)
        return

    #disconnect event
    elif event["type"] == "disconnect":
      # find what node we are disconnecting
      gn1 = self.node_dict[event["hub"]]
      # find what strut we are disconnecting from
      strut = self.socket_dict[(event["hub"],event["socket"])]
      # find the other end of the strut and disconnect
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
        # nothing at the other end of the strut
        print "Receive effectless disconnect event:  %s(%d)" % (gn1.label,gn1.unique)
        return

    # configure event does nothing
    elif event["type"] == "configure":
      pass

    # do the filtering
    self.isomorphism_list = map(self.map_isomorphisms, self.isomorphism_list)
    self.isomorphism_list = filter(self.filter_isomorphisms, self.isomorphism_list)

    #print possible molecules
    print "Possible molecules (%d):" % len(self.isomorphism_list)
    self.isomorphism_list.sort(key=self.molecule_key)
    self.set_gui_list(self.isomorphism_list)
    for el in self.isomorphism_list:
      print "%s," % el[0],
    print ""
    #find exact match
    gm = GM.Graph_Matcher(self.isomorphism_list[0][1], self.iso_graph)
    if gm.has_isomorphism():
      print "You have %s." % self.isomorphism_list[0][0]
    print "\n"

# load a pubchem xml file
def import_molecule (name):
  print "Importing %s..." % name,
  g = XP.parse_file("./molecule_data/" + name)
  print "done."
  #strip .xml from the name, add name * graph * iso_map to list
  return (name[0:-4],g,{})

#XXX __init__ magic?
def start(set_listbox, list_observer):
    # import molecule data
    data_files = os.listdir ("./molecule_data")
    
    molecule_list = map (import_molecule, data_files, )
    print ""

    # set up daemons
    sensor_queue = Queue()
    assembly_queue = Queue()

    sensor_demon = Sensor_Demon( sensor_queue, serial_port="/dev/ttyUSB0" )
    assembly_demon = Assembly_Demon( sensor_queue, assembly_queue )
    sensor_demon.start()
    assembly_demon.start()

    app = Molecules( assembly_queue, molecule_list, set_listbox, list_observer)

#    assembly_queue.put({"type": "create",
#                        "hub": (88,1)})

#    assembly_queue.put({"type": "create",
#                        "hub": (42,3)})
#
#    assembly_queue.put({"type": "create",
#                        "hub": (42,4)})
#
#    assembly_queue.put({ "type":    "connect",
#                         "hub":     ( 42, 3 ),
#                         "socket":  0,
#                         "strut":   ( 3, 17 ),
#                         "ball":    0 })
#
#    assembly_queue.put({ "type":    "connect",
#                         "hub":     ( 88, 1 ),
#                         "socket":  0,
#                         "strut":   ( 3, 17 ),
#                         "ball":    1 })
#
#    assembly_queue.put({ "type":    "connect",
#                         "hub":     ( 42, 4 ),
#                         "socket":  0,
#                         "strut":   ( 3, 18 ),
#                         "ball":    0 })
#
#    assembly_queue.put({ "type":    "connect",
#                         "hub":     ( 88, 1 ),
#                         "socket":  1,
#                         "strut":   ( 3, 18 ),
#                         "ball":    1 })
#
#    assembly_queue.put({ "type":    "disconnect",
#                         "hub":     ( 42, 3 ),
#                         "socket":  0})
#
#    assembly_queue.put({"type": "destroy",
#                        "hub": (42,3)})

    return app
