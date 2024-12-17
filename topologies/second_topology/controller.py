from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
#from slices.first_slice import get_first_slice
from utility import get_mac_dict
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
import subprocess
from ryu.lib.packet import packet, ethernet, ether_types, ipv4, udp, tcp, icmp

QUEUE_TCP = 123 # TCP traffic on port 80 is usually  HTTP
QUEUE_UDP = 234 # UDP traffic on port 53 is usually for DNS
QUEUE_ICMP = 345 # ICMP traffic is for ping, its bandwidth is not detectable directly so we could change it?

class SecondSlicing(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    def __init__(self, *args, **kwargs):
        super(SecondSlicing, self).__init__(*args, **kwargs)
        mac_dict = get_mac_dict()

        # self.mac_to_port = {
        #     1: { mac_dict["h1"]: 1, mac_dict["h2"]: 2, mac_dict["h3"]: 3, mac_dict["h4"]: 3, mac_dict["h5"]: 3, mac_dict["h6"]: 3, mac_dict["h7"]: 3, mac_dict["h8"]: 4, mac_dict["h9"]: 4, mac_dict["h10"]: 4 },
        #     2: { mac_dict["h1"]: 4, mac_dict["h2"]: 4, mac_dict["h3"]: 1, mac_dict["h4"]: 2, mac_dict["h5"]: 3, mac_dict["h6"]: 5, mac_dict["h7"]: 5, mac_dict["h8"]: 6, mac_dict["h9"]: 6, mac_dict["h10"]: 6 },
        #     3: { mac_dict["h1"]: 3, mac_dict["h2"]: 3, mac_dict["h3"]: 3, mac_dict["h4"]: 3, mac_dict["h5"]: 3, mac_dict["h6"]: 1, mac_dict["h7"]: 2, mac_dict["h8"]: 3, mac_dict["h9"]: 3, mac_dict["h10"]: 3 },
        #     4: { mac_dict["h1"]: 4, mac_dict["h2"]: 4, mac_dict["h3"]: 5, mac_dict["h4"]: 5, mac_dict["h5"]: 5, mac_dict["h6"]: 5, mac_dict["h7"]: 5, mac_dict["h8"]: 1, mac_dict["h9"]: 2, mac_dict["h10"]: 3 },
        # }

        self.slice_to_port = {
            3: { 1: [3], 3: [1, 2], 2: [3]},
            2: { 5: [3, 2], 3: [5], 2: [5]}
            #1: { 1: [3], 3: [1] },
            #2: { 4: [5, 1], 5: [4,3], 3: [5], 1: [4] },
            #3: { 1: [2,3], 2: [1,3], 3: [1,2] }
        }
        #print("First configuration loaded:", self.slice_to_port)

        self.queue_exists = {}
        # Dictionary that stores dpid (keys), ports (key, value) with all queues ID active for them (values)

    
    #TO DO: Add a function that every time the server send a requests, change the size of the queues by executing a bash script and passing to it as variables the size of the queues
    
    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install the table-miss flow entry.
        match = parser.OFPMatch()
        actions = [
            parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)
        ]
        # the table-miss flow entry has priority 0 so that it only matches when no other flow entries match
        self.add_flow(datapath, 0, match, actions)

        for port_no in range(1, 6):  # Request queue config for each port
            self.request_queue_config(datapath, port_no)

    def request_queue_config(self, datapath, port_no):
        parser = datapath.ofproto_parser
        req = parser.OFPQueueGetConfigRequest(datapath, port=port_no)
        datapath.send_msg(req) # Send the request message for queue config, that runs the function under this

    @set_ev_cls(ofp_event.EventOFPQueueGetConfigReply, MAIN_DISPATCHER)
    def handle_queue_config_reply(self, ev):
        msg = ev.msg
        dpid = msg.datapath.id
        port_no = msg.port
        queues = msg.queues
        print(dpid, " ", port_no, ": ", queues)
        if dpid not in self.queue_exists:
            self.queue_exists[dpid] = {}
        self.queue_exists[dpid][port_no] = [queue.queue_id for queue in queues]
        
        # Verify that a queue exist for a given port, otherwise if the queue doesn't exist the packet would be dropped

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # construct flow_mod message and send it.
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=datapath, priority=priority, match=match, instructions=inst
        )
        datapath.send_msg(mod)

    def _send_package(self, msg, datapath, in_port, actions):
        data = None
        ofproto = datapath.ofproto
        if msg.buffer_id == ofproto.OFP_NO_BUFFER:
            data = msg.data

        out = datapath.ofproto_parser.OFPPacketOut(
            datapath=datapath,
            buffer_id=msg.buffer_id,
            in_port=in_port,
            actions=actions,
            data=data,
        )
        datapath.send_msg(out)

    # COPIED FROM GRANELLI

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        in_port = msg.match['in_port']
        ofp_parser = datapath.ofproto_parser # contains the parser
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        # ip_pkt = pkt.get_protocol(ipv4.ipv4) # If we want to change and add IP as a service
        tcp_pkt = pkt.get_protocol(tcp.tcp)
        udp_pkt = pkt.get_protocol(udp.udp)
        icmp_pkt = pkt.get_protocol(icmp.icmp)

        src = eth.src
        dst = eth.dst

        out_ports = self.slice_to_port.get(datapath.id, {}).get(in_port, [])
        actions = [ ]

        if tcp_pkt and tcp_pkt.dst_port == 80:
            # HTTP traffic
            print("HTTP traffic")
            for out_port in out_ports:
                if QUEUE_TCP in self.queue_exists[datapath.id].get(out_port, []):
                    actions.append(ofp_parser.OFPActionSetQueue(QUEUE_TCP)) # If the given QUEUE_ID is associated with the port, add the action otherwise no
                actions.append(ofp_parser.OFPActionOutput(out_port))
            match = ofp_parser.OFPMatch( # Create match rule for Flow Table
                in_port=in_port,
                eth_dst=dst,
                eth_type=ether_types.ETH_TYPE_IP,
                ip_proto=0x06, 
                tcp_dst=80,
            )
            self.add_flow(datapath, 1, match, actions)
            self._send_package(msg, datapath, in_port, actions)
        elif udp_pkt and udp_pkt.dst_port == 53:
            # DNS traffic
            print("DNS detected")
            for out_port in out_ports:
                if QUEUE_UDP in self.queue_exists[datapath.id].get(out_port, []):
                    actions.append(ofp_parser.OFPActionSetQueue(QUEUE_UDP)) 
                actions.append(ofp_parser.OFPActionOutput(out_port))
            match = ofp_parser.OFPMatch( 
                in_port=in_port,
                eth_dst=dst,
                eth_type=ether_types.ETH_TYPE_IP,
                ip_proto=0x11, 
                udp_dst=53,
            )    
            self.add_flow(datapath, 1, match, actions)
            self._send_package(msg, datapath, in_port, actions)
        elif icmp_pkt:
            # ICMP traffic
            print("ICMP traffic")
            for out_port in out_ports:
                if QUEUE_ICMP in self.queue_exists[datapath.id].get(out_port, []):
                    print("Associo coda")
                    actions.append(ofp_parser.OFPActionSetQueue(QUEUE_ICMP))
                actions.append(ofp_parser.OFPActionOutput(out_port))
            match = ofp_parser.OFPMatch( 
                in_port=in_port,
                eth_dst=dst,
                eth_type=ether_types.ETH_TYPE_IP,
                ip_proto=0x01, 
            )
            self.add_flow(datapath, 1, match, actions)
            self._send_package(msg, datapath, in_port, actions)
        else: 
            print("General traffic")
            for out_port in out_ports:
                actions.append(ofp_parser.OFPActionOutput(out_port))
            match = datapath.ofproto_parser.OFPMatch(
                in_port=in_port,
                eth_dst=dst,
                eth_type=ether_types.ETH_TYPE_IP,
            )
            self.add_flow(datapath, 1, match, actions)
            self._send_package(msg, datapath, in_port, actions)

            

        

        
        
        