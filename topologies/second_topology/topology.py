from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel
from qos import QoS

HTTP_SIZE = "4" + "0" * 6 # 4Mbps
DNS_SIZE = "2" + "0" * 6
ICMP_SIZE = "3" + "0" * 6

class SecondTopology(Topo):
    """
    SecondTopology class defines the network topology for the second scenario.
    It includes 10 hosts and 4 switches with specific link configurations.
    """
    def __init__(self):
        """
        Build the custom topology.
        """
        # Initialize topology
        Topo.__init__(self)

        link_config = dict()
        host_link_config = dict()

        # Add hosts
        host_list = dict(inNamespace=True)
        for i in range(10):
            self.addHost("h%s" % (i + 1), **host_list)

        # Add switches
        for i in range(4):
            sconfig = {"dpid": "%016x" % (i + 1)}
            self.addSwitch("s%s" % (i + 1), **sconfig)

        # Add host links
        self.addLink("h1", "s1", **link_config)
        self.addLink("h2", "s1", **link_config)
        self.addLink("h3", "s2", **link_config)
        self.addLink("h4", "s2", **link_config)
        self.addLink("h5", "s2", **link_config)
        self.addLink("h6", "s3", **link_config)
        self.addLink("h7", "s3", **link_config)
        self.addLink("h8", "s4", **link_config)
        self.addLink("h9", "s4", **link_config)
        self.addLink("h10", "s4", **link_config)

        # Add switch links
        self.addLink("s1", "s2", **host_link_config)
        self.addLink("s1", "s4", **host_link_config)
        self.addLink("s2", "s3", **host_link_config)
        self.addLink("s2", "s4", **host_link_config)

topos = {"sdn_slicing_second": (lambda: SecondTopology())}

if __name__ == "__main__":
    # Set the log level to info
    setLogLevel("info")
    topo = SecondTopology()
    # Create the network
    net = Mininet(
        topo = topo,
        switch = OVSKernelSwitch,
        build = False,
        autoSetMacs = True,
        autoStaticArp = True,
        link = TCLink
    )
    # Create and add the controller to the network
    controller = RemoteController("c0", ip="127.0.0.1", port = 6633)
    net.addController(controller)

    # Build and start the network
    net.build()
    net.start()

    qos = QoS()
    qos.start_process(HTTP_SIZE, DNS_SIZE, ICMP_SIZE)

    CLI(net)

    net.stop()