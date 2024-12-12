from mininet.topo import Topo
from mininet.net import Mininet
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.cli import CLI
from mininet.link import TCLink


class NetworkSlicingTopo(Topo):
    def __init__(self):
        Topo.__init__(self)

        host_config = dict(inNamespace=True)

        for i in range(5):
            sconfig = {"dpid": "%016x" % (i + 1)}
            self.addSwitch("s%d" % (i + 1), **sconfig)

        for i in range(9):
            self.addHost("h%d" % (i + 1), **host_config)

        self.addLink("s1", "s2", bw=1)
        self.addLink("s1", "s3", bw=10)
        self.addLink("s1", "s4", bw=1)
        self.addLink("s1", "s5", bw=10)
        self.addLink("s2", "h5", bw=1)   
        self.addLink("s3", "h2", bw=1)   
        self.addLink("s3", "h3", bw=1)   
        self.addLink("s3", "h4", bw=1)   
        self.addLink("s4", "h6", bw=10)  
        self.addLink("s4", "h7", bw=10)  
        self.addLink("s4", "h8", bw=10)  
        self.addLink("s5", "h1", bw=10)   
        self.addLink("s5", "h9", bw=10)  


topos = {"networkslicingtopo": (lambda: NetworkSlicingTopo())}

if __name__ == "__main__":
    topo = NetworkSlicingTopo()
    net = Mininet(
        topo=topo,
        switch=OVSKernelSwitch,
        build=False,
        autoSetMacs=True,
        autoStaticArp=True,
        link=TCLink,
    )
    controller = RemoteController("c1", ip="127.0.0.1", port=6633)
    net.addController(controller)
    net.build()
    net.start()
    CLI(net)
    net.stop()
