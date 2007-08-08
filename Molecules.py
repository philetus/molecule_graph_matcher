from Queue import Queue

from pyposey.assembly_graph.Assembly_Graph import Assembly_Graph
from pyposey.assembly_graph.Part_Library import Part_Library

from Graph import Graph
from Graph_Node import Graph_Node

from Simple_Hub import Simple_Hub
from Simple_Strut import Simple_Strut

class Molecules:
  def __init__ (self, event_queue, isomorphism_list ):
    self.isomorphism_lists = isomorphism_list
    self.part_library = Part_Library( hub_class=Simple_Hub,
                                     strut_class=Simple_Strut )
    self.assembly_graph = Assembly_Graph( event_queue=event_queue,
                                              part_library=self.part_library )
    self.iso_graph = Graph()
    self.node_dict = {}

    self.assembly_graph.start()

    self.assembly_graph.observers.append( self.update_isomorphisms )


  def update_isomorphisms( self ):
    self.assembly_graph.lock.acquire()
    event = self.assembly_graph.event_queue.get()

    if event["type"] == "create":
      gn = Graph_Node(event["hub"])
      self.node_dict[event["hub"]] = gn
      self.iso_graph.add_node(gn)

    elif["type"] == "destroy":
      self.iso_graph.remove_node(gn)
      del self.node_dict[event["hub"]]

    elif event["type"] == "connect":
      gn1 = self.node_dict[event["hub"]]
      gn2 = self.node_dict[event["strut"]]
      self.iso_graph.add_edge(gn1, gn2)

    elif event["type"] == "disconnect":
      gn1 = self.node_dict[event["hub"]]
      gn2 = self.node_dict[event["strut"]]
      self.iso_graph.add_edge(gn1, gn2)

    elif["type"] == "configure":
      pass

    self.assembly_graph.lock.release()


if __name__ == "__main__":
    assembly_queue = Queue()
    molecule_list = []

    app = Molecules( assembly_queue, molecule_list )

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
                         "hub":     ( 42, 4 ),
                         "socket":  0,
                         "strut":   ( 3, 17 ),
                         "ball":    1 })
 
