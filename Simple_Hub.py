from pyposey.assembly_graph.Hub import Hub

class Simple_Hub( Hub ):
    """
    """

    def __init__( self, address, children, part_type, rootness ):
        """
        """
        Hub.__init__( self, address, children, part_type, rootness )

    def write( self ):
        print ("I am hub (%d,%d)." % self.address)
