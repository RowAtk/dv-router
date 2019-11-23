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
    
    def update(self, x, latency):
        name = api.get_name(x)
        if self.isNode(x):
            self.latencies[name] = latency
        else:
            self.add(x, latency)

    def isNode(self, v):
        return v in self.latencies

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

    def __repr__(self):
        string = ""
        for vname, latencies in self.vectors:
            string += "%s: <%s>\n" % (vname, str(latencies)) 
        return string

class RTable:
    def __init__(self, x={}):
        self.table = x

    def add(self, interface, port):
        self.table[interface] = port

    def isEntry(self, src):
        return src in self.table

    def get(self, interface):
        return self.table[interface]

    def __repr__(self):
        string = "RTABLE Entries\n"
        for i, p in self.table:
            string += "%s -> port %s\n" % (i, p)
        return string


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
        
        self.speak("Incoming packet: %s | src: %s | dest: %s | port: %s | trace: %s" % (str(type(packet)).split('.')[-1], src, dest, port, packet.trace))

        #self.log("RX %s on %s (%s)", packet, port, api.current_time())
        if isinstance(packet, basics.RoutePacket):
            self.dv_matrix.get(src).update(dest)
            pass
        elif isinstance(packet, basics.HostDiscoveryPacket) or not self.rtable.isEntry(src):
            self.discover(src, port)
        else:
            # Totally wrong behavior for the sake of demonstration only: send
            # the packet back to where it came from!
            # self.send(packet, port=port)
            if not self.is_for_me(dest):
                if self.rtable.isEntry(dest):
                    # destination is known
                    self.speak("%s is known" % (dest))
                    self.send(packet, self.get_out_port(dest))
                else:
                    # destination is unknown
                    self.speak("%s is unknown to me" % (dest))
            else:
                self.speak("packet has no destination or is... FOR ME!!")


                       

            

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
        if not self.rtable.isEntry(src):
            self.speak("Source entity %s is unknown" % (src))
            self.rtable.add(src, port)
            v = DVector(src)
            self.speak(self.dv_matrix)
            self.dv_matrix.add(v)

    def get_out_port(self, dest):
        return self.rtable.get(dest)

    def speak(self, msg):
        print ("\n%s says: %s\n" % (api.get_name(self.name), msg)) 

    def is_for_me(self, dest):
        return dest and dest == api.get_name(self)
