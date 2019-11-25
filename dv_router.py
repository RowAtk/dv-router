"""Your awesome Distance Vector router for CS 168."""

import sim.api as api
import sim.basics as basics

# We define infinity as a distance of 16.
INFINITY = 16
"""
matrix
    r1 r2
r1
r2

r1: {r1: 0, r2: 3}
"""

class DMatrix:
    def __init__(self, rtable, owner="Unnamed"):
        self.vectors = {}
        self.rtable = rtable
        self.owner = owner

    def changeOwner(self, name):
        self.owner = name

    def replaceName(self, oldname, newname):
        for vname, vector in self.vectors.items():
            if vname == oldname:
                self.vectors[newname] = self.vectors.pop(oldname)
            for key in vector.keys():
                if key == oldname:
                    vector[newname] = vector.pop(oldname)

    def myVector(self):
        return self.get(self.owner)

    def get(self, x):
        try:
            vector = self.vectors[api.get_name(x)]
            return vector
        except KeyError as e:
            return None

    def get_cell(self, x, y):
        """ return latency (cell value) in matrix given src(x) and dest(y) """
        vector = self.get(x)
        if vector:
            try:
                return vector[api.get_name(y)]
            except KeyError as e:
                return None
        return None

    def get_all_cells(self):
        cells = []
        for x, vector in self.vectors.items():
            for y, latency in vector.items():
                cells.append((x, y, latency))

    def delete(self, x, y=None):
        vector = self.vectors[x]
        if y:   # delete single cell
            del vector[y]
        else:   # delete entire vector
            del vector

    def set_cell(self, x, y, val):
        self.vectors[x][y] = val

    def update(self, x, y, val):
        try:
            vectors = self.vectors
            if x in vectors:
                # src of update has entry in matrix
                self.set_cell(x, y, val)
                # self.vectors[x][y] = val
                pass
            else:
                # src is unknown, therefore new entry is made
                self.vectors[x] = {y: val}
            # print "STOP 1\n", self.vectors
            if y not in self.myVector().keys():
                # dest if update is unknown, therefore is introduced to us as unreachable (at first)
                self.set_cell(self.owner,y, INFINITY)
            
        except:
            print "UPDATE ERROR"
        finally:
            # print "STOP 2\n", self.vectors
            self.optimize()
            pass     
    
    def optimize(self):
        """ matrix maximized using bellman ford algo """
        x = self.owner
        # print "STOP 3\n", self.myVector().keys()
        for y in self.myVector().keys():
            if y != x:
                minCost = self.bFord(x, y)
                self.set_cell(x, y, minCost)

    def bFord(self, x, y):
        """ Bellman Ford Algo: Dx(y) = min { c(x,v) + Dv(y)} """
        costs = []
        # hop = None
        for v in self.get(x).keys():
            # print(v)
            if v != x and v != y:
                dxv = self.get_cell(x, v)
                dvy = self.get_cell(v, y)
                # print dxv, dvy
                if dxv == INFINITY or dvy == None or dvy == INFINITY:
                    costs.append((INFINITY, v))
                else:
                    costs.append((dxv + dvy, v))
            else:
                stl_cost = self.get_cell(x, y)
                if stl_cost:
                    costs.append((self.get_cell(x, y), x))

        if costs == []:
            return INFINITY
        else:
            minimum, next_hop = min(costs)
            self.rtable.update((x, y), next_hop)
            return  minimum
        
    
    def filter(self, port):
        pass

    def __repr__(self):
        string = self.owner + " DV MATRIX\n"
        for x, vector in self.vectors.items():
            string += "%s: %i<%s>\n" % (x, len(vector), str(vector)) 
        
        return string + "\n" + str(self.rtable)

class Table:
    def __init__(self, x_axis = "x", y_axis = "y", name = "Unnamed"):
        self.name = name
        self.x_axis = x_axis
        self.y_axis = y_axis
        self.entries = {}

    def update(self, x,y):
        self.entries[x] = y

    def isEntry(self, x):
        return x in self.entries.keys()

    def get(self, x):
        try:
            return self.entries[x]
        except KeyError as e:
            return None

    def xdelete(self, x):
        del self.entries[x]
    
    def ydelete(self, val):
        for x, y in self.entries.items():
            if y == val:
                self.xdelete(x)
                return x
        return None

    def __repr__(self):
        string = "%s TABLE Entries\n" % (self.name)
        for x, y in self.entries.items():
            string += "%s %s -> %s %s\n" % (self.x_axis, x, self.y_axis, y)
        return string


class DVRouter(basics.DVRouterBase):
    # NO_LOG = True # Set to True on an instance to disable its logging
    # POISON_MODE = True # Can override POISON_MODE here
    # DEFAULT_TIMER_INTERVAL = 5 # Can override this yourself for testing

    def __init__(self):
        
        self.start_timer()  # Starts calling handle_timer() at correct rate
        # Tables
        self.platencies = Table(x_axis="port", y_axis="latency", name="port latency")
        self.ftable = Table(x_axis="host", y_axis="port", name="forwarding")
        self.rtable = Table(x_axis="route", y_axis="next hop", name="Routing")

        self.dv_matrix = DMatrix(rtable=self.rtable)

    def handle_link_up(self, port, latency):
        
        # housekeeping due to naming issues before start of simulator
        if not self.dv_matrix.get(self.name):
            self.dv_matrix.changeOwner(self.name)
            self.dv_matrix.update(self.name, self.name, 0)

        # print self.dv_matrix    

        self.platencies.update(port, latency)
        pass

    def handle_link_down(self, port):
        self.platencies.update(port, INFINITY)
        # delete entry from ftable
        lost_entity = self.ftable.ydelete(port)
        
        if lost_entity:
            # change latency in matrix
            if self.rtable.get((self.name, lost_entity)) == lost_entity:
                self.dv_matrix.update(self.name, lost_entity, INFINITY)

        pass

    def handle_rx(self, packet, port):
       
        # extract source and destination from packet
        src, dest = self.getOrigins(packet)
        
        # self.speak("Incoming packet: %s | src: %s | dest: %s | port: %s | trace: %s" % (str(type(packet)).split('.')[-1], src, dest, port, packet.trace))

        #self.log("RX %s on %s (%s)", packet, port, api.current_time())
        if isinstance(packet, basics.RoutePacket):
            
            # if not self.ftable.isEntry(src):                                    # update forwarding table (switch entry)
            #     self.ftable.update(src, port)
           

            if src not in self.dv_matrix.myVector().keys():   
                self.dv_matrix.set_cell(self.name, src, self.platencies.get(port))    # update my own vector
            self.dv_matrix.update(src, dest, packet.latency)                        # update any other vector

        elif isinstance(packet, basics.HostDiscoveryPacket):
            # self.discover(self.hr_table, src, port)
            # self.ftable.update(src, port)
            if not self.ftable.isEntry(src):                                    # update forwarding table (switch entry)
                self.ftable.update(src, port)

            # self.speak(self.platencies.get(port))
            # self.dv_matrix.update(self.name, src, self.platencies.get(port))
            # self.speak(self.dv_matrix)
            pass

        else:   # Data Packet or Ping
            # self.speak("Incoming packet: %s | src: %s | dest: %s | port: %s | trace: %s" % (str(type(packet)).split('.')[-1], src, dest, port, packet.trace))
            # self.speak("\n%s\n%s" % (self.ftable, self.dv_matrix))
            if dest == self.name:
                self.speak("I GOT YOUR PACKET")
                pass
            elif self.ftable.isEntry(dest):
                out_port = self.ftable.get(dest)
                self.speak("GOT PACKET, SEND OUT ON PORT: %s" % out_port)
                self.send(packet, port=out_port)
            else:
                self.speak("NOT IN F TABLE")
                next_hop = self.rtable.get((self.name, dest))
                if next_hop:
                    out_port = self.ftable.get(next_hop)
                    self.send(packet, port=out_port)
                else:
                    self.speak("NO NEXT HOP")


                                

    def handle_timer(self):
        """
        Called periodically.

        When called, your router should send tables to neighbors.  It
        also might not be a bad place to check for whether any entries
        have expired.
        """

        # self.speak(self.dv_matrix.vectors)
        # self.speak("TIMER TRIGGERED\n%s\n%s" % (self.ftable, self.dv_matrix))
        self.send_matrix()

    def send_matrix(self):
        # self.speak(self.dv_matrix)
        for dest, cost in self.dv_matrix.myVector().items():
            self.send(basics.RoutePacket(destination=dest, latency=cost), flood=True)
        


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
