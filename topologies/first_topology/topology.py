from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.link import TCLink

class NetworkTopology(Topo):

    def __init__(self):

        # Initialize topology
        Topo.__init__(self)

        # Create host nodes
        for i in range(1, 11):
            self.addHost(
                f"h{i}",
                inNamespace=True,
                ip=f"192.168.0.{i}/24",  
                mac=f"00:00:00:00:00:{i:02x}"
            )

        # Create switch nodes
        for i in range(1,6):
            sconfig = {"dpid": "%016x" % i}
            self.addSwitch("s%d" % i, **sconfig)

        # Connect switchs
        self.addLink("s1", "s2", port1=1, port2=1, bw=1)
        self.addLink("s1", "s4", port1=2, port2=1, bw=10)
        self.addLink("s2", "s3", port1=2, port2=1, bw=1)
        self.addLink("s2", "s4", port1=3, port2=2, bw=10)
        self.addLink("s3", "s4", port1=2, port2=3, bw=10)
        self.addLink("s4", "s5", port1=4, port2=1, bw=10)

        # Connect hosts and switchs
        self.addLink("s1", "h1", port1=3, port2=1, bw=10)
        self.addLink("s1", "h10", port1=4, port2=1, bw=10)
        self.addLink("s2", "h5", port1=4, port2=1, bw=10)
        self.addLink("s3", "h2", port1=3, port2=1, bw=10)
        self.addLink("s3", "h3", port1=4, port2=1, bw=10)
        self.addLink("s3", "h4", port1=5, port2=1, bw=10)
        self.addLink("s5", "h6", port1=2, port2=1, bw=10)
        self.addLink("s5", "h7", port1=3, port2=1, bw=10)
        self.addLink("s5", "h8", port1=4, port2=1, bw=10)
        self.addLink("s5", "h9", port1=5, port2=1, bw=10)

if __name__ == "__main__":
    # Create an istance of the topology and controller
    topology = NetworkTopology()
    controller = RemoteController("c1", ip="127.0.0.1", port=6633)
    # Create the network    
    net = Mininet(
        topo=topology,
        link=TCLink,
        autoSetMacs=False,
        autoStaticArp=True,
        controller=controller,
    )
    net.start()
    CLI(net)
    net.stop()
