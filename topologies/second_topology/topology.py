from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel

class SecondTopology(Topo):
    def __init__(self):
        # Initialize topology
        Topo.__init__(self)

        high_bw = dict()
        low_bw = dict()
        host_link = dict()

        # Add hosts
        host_list = dict(inNamespace=True)
        for i in range(10):
            self.addHost("h%s" % (i + 1), **host_list)

        # Add switches
        for i in range(4):
            sconfig = {"dpid": "%016x" % (i + 1)}
            self.addSwitch("s%s" % (i + 1), **sconfig)

        # Add host links
        self.addLink("h1", "s1")
        self.addLink("h2", "s1")
        self.addLink("h3", "s2")
        self.addLink("h4", "s2")
        self.addLink("h5", "s2")
        self.addLink("h6", "s3")
        self.addLink("h7", "s3")
        self.addLink("h8", "s4")
        self.addLink("h9", "s4")
        self.addLink("h10", "s4")

        # Add switch links
        self.addLink("s1", "s2", **high_bw)
        self.addLink("s1", "s4", **high_bw)
        self.addLink("s2", "s3", **low_bw)
        self.addLink("s2", "s4", **high_bw)

topos = {"sdn_slicing_second": (lambda: SecondTopology())}

if __name__ == "__main__":
    setLogLevel("info")
    topo = SecondTopology()
    net = Mininet(
        topo = topo,
        switch = OVSKernelSwitch,
        build = False,
        autoSetMacs = True,
        autoStaticArp = True,
        link = TCLink
    )

    controller = RemoteController("c0", ip="127.0.0.1", port = 6633)
    net.addController(controller)

    net.build()
    net.start()

    CLI(net)

    net.stop()