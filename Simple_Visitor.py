from Simple_Strut import Simple_Strut

from pyposey.util.Log import Log

class Simple_Visitor:
    LOG = Log( name='molecules.Simple_Visitor', level=Log.INFO )
    
    def __init__( self, assembly_graph, fun ):
        """
        """

        # assembly graph to visit
        self.graph = assembly_graph
        #function to call
        self.fun = fun
        # nodes visited during rendering for avoiding cycles
        self.visited = None

    def visit( self ):
        """traverse graph and call a function on its nodes
        """
        # acquire assembly graph lock before traversing graph
        self.graph.lock.acquire()
        try:
            # visit each subgraph's root hub
            for hub in ( subgraph.root for subgraph in self.graph.subgraphs ):
                #initialize visited set
                self.visited = set()

                try:
                    self.visit_hub( hub )
                except Exception, error:
                    self.LOG.error( error )

                # deinitialize visited set
                self.visited = None

            print " "

        finally:
            self.graph.lock.release()

    def visit_hub( self, hub ):
        """visit hub and visit its children
        """
        self.LOG.debug(  "visiting hub ", hub.address )
        
        # add to visited set
        self.visited.add( hub )
        
        # visit hub
        getattr(hub, self.fun)()

        # visit children
        for socket in hub.sockets:
            ball = socket.ball
            if (ball is not None) and (ball.strut not in self.visited):
                # visit strut
                self.visit_strut( ball.strut )

    def visit_strut( self, strut, ):
        """ visit strut and its children
        """
        self.LOG.debug(  "visiting strut ", strut.address )
        
        # add to visited set
        self.visited.add( strut )

        # visit strut
        getattr(strut, self.fun)()

        # visit children
        for ball in strut.balls:
            socket = ball.socket
            if (socket is not None) and (socket.hub not in self.visited):

                # visit hub
                self.visit_hub( socket.hub )

