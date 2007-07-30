from Queue import Queue

from pyposey.assembly_graph.Assembly_Graph import Assembly_Graph
from pyposey.assembly_graph.Part_Library import Part_Library

from Simple_Hub import Simple_Hub
from Simple_Strut import Simple_Strut

from Simple_Visitor import Simple_Visitor

class Molecules:
  def __init__ (self, event_queue):
    self.part_library = Part_Library( hub_class=Simple_Hub,
                                     strut_class=Simple_Strut )
    
    self.assembly_graph = Assembly_Graph( event_queue=event_queue,
                                              part_library=self.part_library )
    self.assembly_graph.start()

    self.write_visitor = Simple_Visitor( self.assembly_graph, "write" )
    self.assembly_graph.observers.append( self.write_visitor.visit )


if __name__ == "__main__":
    assembly_queue = Queue()
    
    app = Molecules( event_queue=assembly_queue )

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
 
