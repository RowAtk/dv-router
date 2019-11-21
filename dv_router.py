"""Your awesome Distance Vector router for CS 168."""

import sim.api as api
import sim.basics as basics

# We define infinity as a distance of 16.
INFINITY = 16

class DVector:
    def __init__(self, x):
        name = api.get_name(x)
        self.src = name
        self.latencies = { name: 0 }

    def add(self, x, latency):
        self.latencies[api.get_name(x)] = latency
    """
    def update(self, x, latency):
        name = api.get_name(x)
        # if name in self. 
    """

    def get(self, x):
        return self.latencies[api.get_name(x)]

class DMatrix:
    def __init__(self, x={}):
        self.vectors = x

    def add(self, vector):
        self.vectors[vector.src] = vector.latencies
        
    def get(self, x):
        return self.vectors[api.get_name(x)]

    def get_cell(self, x,y):
        return self.vectors[api.get_name(x)].get(y)
    
    def filter(self, port):
        pass

class RTable:
    def __init__(self, x={}):
        self.table = x

    def add(self, interface, port):
        self.table[interface] = port


class DVRouter(basics.DVRouterBase):
    # NO_LOG = True # Set to True on an instance to disable its logging
    # POISON_MODE = True # Can override POISON_MODE here
    # DEFAULT_TIMER_INTERVAL = 5 # Can override this yourself for testing

    def __init__(self):
        """
        Called when the instance is initialized.

        You probably want to do some additional initialization here.

        """
        self.start_timer()  # Starts calling handle_timer() at correct rate
        self.platencies = {}
        self.rtable = RTable()
        self.dv_matrix = DMatrix()
        self.INFINITY = INFINITY

    def handle_link_up(self, port, latency):
        """
        Called by the framework when a link attached to this Entity goes up.

        The port attached to the link and the link latency are passed
        in.

        """
        self.platencies[port] = latency
        # self.rtable.add(port)   
        pass

    def handle_link_down(self, port):
        """
        Called by the framework when a link attached to this Entity does down.

        The port number used by the link is passed in.

        """
        self.platencies[port] = self.INFINITY
        pass

    def handle_rx(self, packet, port):
        """
        Called by the framework when this Entity receives a packet.

        packet is a Packet (or subclass).
        port is the port number it arrived on.

        You definitely want to fill this in.

        """

        # extract source and destination from packet
        src, dest = self.getOrigins(packet)

        #self.log("RX %s on %s (%s)", packet, port, api.current_time())
        if isinstance(packet, basics.RoutePacket):
            self.dv_matrix
            pass
        elif isinstance(packet, basics.HostDiscoveryPacket) or not self.isEntry(src):
            self.discover(src, port)
        else:
            # Totally wrong behavior for the sake of demonstration only: send
            # the packet back to where it came from!
            # self.send(packet, port=port)
            if not self.is_for_me(dest):
                if self.isEntry(dest):
                    # destination is known
                    self.speak(f"{dest} is a known")
                    self.send(packet, self.get_port(dest))
                else:
                    # destination is unknown
                    self.speak(f"{dest} is unknown to me")
            else:
                print("packet has no destination or is... FOR ME!!")


                       

            

    def handle_timer(self):
        """
        Called periodically.

        When called, your router should send tables to neighbors.  It
        also might not be a bad place to check for whether any entries
        have expired.

        """
        pass


    def update_matrix(self):
        pass

    def update_rtable(self):
        pass

    def optimal_route(self, vector):
        pass

    def getOrigins(self, packet):
        src = api.get_name(packet.src)

        # RoutePacket uses "destination" instead of "dst"
        if isinstance(packet, basics.RoutePacket):
            dest = api.get_name(packet.destination)
        else:
            dest = api.get_name(packet.dst)

        return src, dest

    def discover(self, src, port):
        if src not in self.rtable:
            self.speak(f"Source entity: {src} is unknown")
            self.rtable.add(src, port)
            self.dv_matrix.add(DVector(src))

    def isEntry(self, src):
        return src in self.rtable

    def get_port(self, dest):
        return self.rtable[dest]

    def speak(self, msg):
        print(api.get_name(self.name), "says:", msg)

    def is_for_me(self, dest):
        return dest and dest == api.get_name(self)
