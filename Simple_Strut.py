from pyposey.assembly_graph.Strut import Strut

class Simple_Strut( Strut ):
    """
    """

    def __init__( self, address, children, part_type, rootness ):
        """
        """
        Strut.__init__( self, address, children, part_type, rootness )
        
    def write( self ):
        print ("I am strut (%d,%d)." % self.address)
