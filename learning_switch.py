"""
Your learning switch warm-up exercise for CS-168.

Start it up with a commandline like...

  ./simulator.py --default-switch-type=learning_switch topos.rand --links=0

"""

import sim.api as api
import sim.basics as basics

class TableEntry(object):
    
    def __init__(self, netId, port, weight = None):
        self.netId = netId
        self.out_port = port
        self.weight = weight


class LearningSwitch(api.Entity):
    """
    A learning switch.

    Looks at source addresses to learn where endpoints are.  When it doesn't
    know where the destination endpoint is, floods.

    This will surely have problems with topologies that have loops!  If only
    someone would invent a helpful poem for solving that problem...

    """

    def __init__(self):
        """
        Do some initialization.

        You probablty want to do something in this method.

        """
        self.rtable = {}
        pass

    def handle_link_down(self, port):
        """
        Called when a port goes down (because a link is removed)

        You probably want to remove table entries which are no longer
        valid here.

        """
        for interface, iport in self.rtable.items():
            if iport == port:
                del self.rtable[interface]
                break


    def handle_rx(self, packet, in_port):
        """
        Called when a packet is received.

        You most certainly want to process packets here, learning where
        they're from, and either forwarding them toward the destination
        or flooding them.

        """

        print("Entity:", api.get_name(self), "PACKET RECEIVED: ", packet, "ON PORT:", in_port)

        src, dest = self.getOrigins(packet)
        
        print("PACKET SRC:", src, "DEST:", dest, "TRACE:", packet.trace)

        # The source of the packet can obviously be reached via the input port, so
        # we should "learn" that the source host is out that port.  If we later see
        # a packet with that host as the *destination*, we know where to send it!
        # But it's up to you to implement that.  For now, we just implement a
        # simple hub.

        if isinstance(packet, basics.HostDiscoveryPacket):
            # Don't forward discovery messages
            if src not in self.rtable:
                print("UNKNOWN SOURCE")
                self.rtable[src] = in_port
            return 

        
        # Sender is not known to switch
        if src not in self.rtable:
            print("UNKNOWN SOURCE")
            self.rtable[src] = in_port
        
        # destination properly defined and is not intended for this switch
        if dest and dest != api.get_name(self):
            if dest in self.rtable:
                # destination is a known route
                print("KNOWN ROUTE")
                self.send(packet, self.rtable[dest])
            else:
                # destination is an unknown route
                print("FLOOD")
                self.send(packet, in_port, flood=True)
        else:
            print("packet has no destination or is... FOR ME!!")

    
    def getOrigins(self, packet):
        src = api.get_name(packet.src)

        # RoutePacket uses "destination" instead of "dst"
        if isinstance(packet, basics.RoutePacket):
            dest = api.get_name(packet.destination)
        else:
            dest = api.get_name(packet.dst)

        return src, dest
