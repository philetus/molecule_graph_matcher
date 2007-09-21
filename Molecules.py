#  Main molecule matching file.  It makes a list of graphs of molecule we have
#  a PubChem XML file for.  It also keeps track of a graph representing the
#  current state of the posey pieces.  Then it waits for assembly events.  On
#  an event, the posey graph is updated appropriately, and each the list of
#  possible molecules it matches is filtered by attempting to match the posey
#  graph against each possible molecule graph.

from Queue import Queue

import threading

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
  def __init__ (self, event_queue, isomorphism_list, set_gui_list, update_display):
    # initialize various fields
    # list of possible molecules
    self.isomorphism_list = isomorphism_list
    # a copy of the original possible molecules for backtracking on
    # destroy or disconnect events
    self.original_isomorphism_list = isomorphism_list[:]
    # part data
    self.part_library = Part_Library( hub_class=Hub,
                                     strut_class=Strut )

    # posey graph
    self.iso_graph = Graph()
    # information on currently connected pieces to help update the graph
    self.node_dict = {}
    self.socket_dict = {}
    self.strut_dict = {}

    #setting gui hook
    self.set_gui_list = set_gui_list
    self.update_display = update_display

    # print initial moledcules
    print "Initial possible molecules (%d):" % len(self.isomorphism_list)
    self.isomorphism_list.sort(key=self.molecule_key)
    self.set_gui_list(self.isomorphism_list)
    for el in self.isomorphism_list:
      print "%s,"% el[0],
    print ""
    print "\n"

    #start thread to process assembly events
    t = threading.Thread(target=self.event_wait,args=(event_queue,))
    t.setDaemon(1)
    t.start()
   
  # We sort molecules by size
  def molecule_key (self, m):
    return m[1].adj_matrix.shape[0]

  # Used with map: for each graph in our list, try to
  # match the posey graph to it.
  def map_isomorphisms( self, large ):
    if self.iso_graph.adj_matrix.shape[0] == 0:
      # the graph is empty
      return (large[0], large[1], {})
    if self.iso_graph.adj_matrix.shape[0] > large[1].adj_matrix.shape[0]:
      # return if we are larger than the molecule we are testing against
      return (large[0], large[1], None)
    gm = GM.Graph_Matcher(large[1], self.iso_graph)
    iso_map = gm.get_isomorphism()
    return (large[0], large[1], iso_map)


  # Used with filter to get rid of failed matches.
  def filter_isomorphisms( self, triple ):
    return triple[2] is not None


  # wait for events, update the iso graph
  def event_wait (self, event_queue):
    while 1:
      self.update_isomorphisms(event_queue.get())


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
      try:
        gn = self.node_dict[event["hub"]]
        print "Received destroy event: %s(%d)" % (gn.label, gn.unique)
        # remove node from graph
        self.iso_graph.remove_node(gn)
        # remove node from dictionary
        del self.node_dict[event["hub"]]
        # replace molecule list with original list
        # This requires some explanation. Since we filter out unmatching graphs,
        # our list of matching molecules gets smaller monotonically.  When we
        # need to make our list larger on destroy or disconnect, we refilter the
        # whole list.
        self.isomorphism_list = self.original_isomorphism_list[:]
      except KeyError:
        # We can't find this node; probably a hardware infelicity
        print "WARNING: Unable to understand destroy event."
        print self.iso_graph
        return

    # connect event
    elif event["type"] == "connect":
      try:
        # find what node we are connecting
        gn1 = self.node_dict[event["hub"]]
        # find what strut we are connecting to.
        strut = self.part_library[event["strut"]]
        # record this strut is in our graph
        self.socket_dict[(event["hub"],event["socket"])] = strut
        # find the node at the other end of the strut and connect to it
        hub_addresses = None
        if strut in self.strut_dict:
          hub_addresses = self.strut_dict[strut]
        else:
          hub_addresses = set()
        flag = 0
        for hub_address in hub_addresses:
          if hub_address != event["hub"]:
            gn2 = self.node_dict[hub_address]
            print "Received connect event: %s(%d) <--> %s(%d)" % (gn1.label,gn1.unique,gn2.label,gn2.unique)
            self.iso_graph.add_edge(gn1, gn2)
            flag = 1
            break
        hub_addresses.add(event["hub"])
        self.strut_dict[strut] = hub_addresses
        if not flag:
          # no node at the other end of the strut
          print "Receive effectless connect event:  %s(%d)" % (gn1.label,gn1.unique)
          print self.iso_graph
          return
      except KeyError:
        print "WARNING: Unable to understand connect event."
        print self.iso_graph
        return

    #disconnect event
    elif  event["type"] == "disconnect":
      try:
        # find what node we are disconnecting
        gn1 = self.node_dict[event["hub"]]
        # find what strut we are disconnecting from
        strut = self.socket_dict[(event["hub"],event["socket"])]
        # find the other end of the strut and disconnect
        hub_addresses = None
        if strut in self.strut_dict:
          hub_addresses = self.strut_dict[strut]
        else:
          hub_addresses = set()
        flag = 0
        for hub_address in hub_addresses:
          if hub_address != event["hub"]:
            gn2 = self.node_dict[hub_address]
            print "Received disconnect event: %s(%d) <-/-> %s(%d)" % (gn1.label,gn1.unique,gn2.label,gn2.unique)
            self.iso_graph.remove_edge(gn1, gn2)
            self.isomorphism_list = self.original_isomorphism_list[:]
            flag = 1
            break
        try:
          hub_addresses.remove(event["hub"])
        except KeyError:
          pass
        self.strut_dict[strut] = hub_addresses
        if not flag:
          # nothing at the other end of the strut
          print "Receive effectless disconnect event:  %s(%d)" % (gn1.label,gn1.unique)
          print self.iso_graph
          return
      except KeyError:
        print "WARNING: Unable to understand connect event."
        print self.iso_graph
        return

    # configure event does nothing
    elif event["type"] == "configure":
      return 
    
    print self.iso_graph

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
    #find exact match (doesn't work)
#    if len(self.isomorphism_list) > 0:
#      gm = GM.Graph_Matcher(self.isomorphism_list[0][1], self.iso_graph)
#      if gm.has_isomorphism():
#        print "You have %s." % self.isomorphism_list[0][0]
#      print "\n"

    self.update_display()

# load a pubchem xml file
def import_molecule (name):
  print "Importing %s..." % name,
  g = XP.parse_file("./molecule_data/" + name)
  print "done."
  #strip .xml from the name, add name * graph * iso_map to list
  return (name[0:-4],g,{})

#XXX __init__ magic?
def start(set_listbox, update_display):
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

    app = Molecules( assembly_queue, molecule_list, set_listbox, update_display)

    return app
