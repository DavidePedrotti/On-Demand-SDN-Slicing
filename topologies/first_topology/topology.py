from comnetsemu.net import Containernet
from comnetsemu.cli import CLI
from mininet.node import OVSKernelSwitch, RemoteController
from mininet.link import TCLink
from mininet.log import setLogLevel

if __name__ == "__main__":
    setLogLevel("info")

    net = Containernet(
        switch=OVSKernelSwitch,
        link=TCLink,
        autoSetMacs=False,
        autoStaticArp=True,
    )

    controller = RemoteController("c1", ip="127.0.0.1", port=6633)
    net.addController(controller)

    # Add switches
    switches = {}
    for i in range(1, 6):
        sconfig = {"dpid": "%016x" % i}
        switches[f"s{i}"] = net.addSwitch(f"s{i}", **sconfig)

    # Add hosts
    hosts = {}
    for i in range(1, 11):
        if i in [6, 9]:  # h6 reception (client) and h9 database (server)
            hosts[f"h{i}"] = net.addDockerHost(
                f"h{i}",
                dimage="dev_test",  
                ip=f"192.168.0.{i}/24",
                docker_args={"hostname": f"h{i}"},
            )
        else:  
            hosts[f"h{i}"] = net.addHost(
                f"h{i}",
                ip=f"192.168.0.{i}/24",
                mac=f"00:00:00:00:00:{i:02x}",
            )

    # Add links
    net.addLink(switches["s1"], switches["s2"], port1=1, port2=1, bw=1)
    net.addLink(switches["s1"], switches["s4"], port1=2, port2=1, bw=10)
    net.addLink(switches["s2"], switches["s3"], port1=2, port2=1, bw=1)
    net.addLink(switches["s2"], switches["s4"], port1=3, port2=2, bw=10)
    net.addLink(switches["s3"], switches["s4"], port1=2, port2=3, bw=10)
    net.addLink(switches["s4"], switches["s5"], port1=4, port2=1, bw=10)

    net.addLink(switches["s1"], hosts["h1"], port1=3, port2=1, bw=10)
    net.addLink(switches["s1"], hosts["h10"], port1=4, port2=1, bw=10)
    net.addLink(switches["s2"], hosts["h5"], port1=4, port2=1, bw=10)
    net.addLink(switches["s3"], hosts["h2"], port1=3, port2=1, bw=10)
    net.addLink(switches["s3"], hosts["h3"], port1=4, port2=1, bw=10)
    net.addLink(switches["s3"], hosts["h4"], port1=5, port2=1, bw=10)
    net.addLink(switches["s5"], hosts["h6"], port1=2, port2=1, bw=10)
    net.addLink(switches["s5"], hosts["h7"], port1=3, port2=1, bw=10)
    net.addLink(switches["s5"], hosts["h8"], port1=4, port2=1, bw=10)
    net.addLink(switches["s5"], hosts["h9"], port1=5, port2=1, bw=10)

    net.start()
    CLI(net)
    net.stop()
