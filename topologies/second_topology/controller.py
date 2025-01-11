from ryu.app.wsgi import ControllerBase, WSGIApplication, route
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, DEAD_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.lib.packet import packet, ethernet, ether_types, ipv4, udp, tcp, icmp
from ryu.ofproto import ofproto_v1_3
from enum import Enum
from utils import slice_to_port
from qos import QoS
from webob import Response
import json

current_modes = []

second_slicing_instance_name = "second_slicing_api_app"
url = "/controller/second"

QUEUE_TCP = 123 # TCP traffic on port 80 is usually  HTTP
QUEUE_UDP = 234 # UDP traffic on port 53 is usually for DNS
QUEUE_ICMP = 345 # ICMP traffic is for ping, its bandwidth is not detectable directly so we could change it?
QUEUE_GT = 456 # General traffic queue


class SecondSlicing(app_manager.RyuApp):
    """
    Ryu application for managing network slicing.
    """    
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    _CONTEXTS = {"wsgi": WSGIApplication}

    def __init__(self, *args, **kwargs):
        super(SecondSlicing, self).__init__(*args, **kwargs)

        self.slice_to_port = slice_to_port()
        self.queue_exists = {}
        self.datapaths = {}

        wsgi = kwargs["wsgi"]
        wsgi.register(SecondSlicingController, {second_slicing_instance_name: self})

    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
        """
        Handle state changes of switches.

        Args:
            ev (EventOFPStateChange): The event representing the state change.

        Returns:
            None
        """        
        datapath = ev.datapath
        if ev.state == MAIN_DISPATCHER:
            self.datapaths[datapath.id] = datapath
            print(f"Switch {datapath.id} connected.")
        elif ev.state == DEAD_DISPATCHER:
            if datapath.id in self.datapaths:
                del self.datapaths[datapath.id]
                print(f"Switch {datapath.id} disconnected.")

    @set_ev_cls(ofp_event.EventOFPSwitchFeatures, CONFIG_DISPATCHER)
    def switch_features_handler(self, ev):
        """
        Handle the switch features event and establish flow entries for packet matching.
        This method creates:
        - A flow entry with priority 0 to forward packets that do not match any existing flow rules to the controller.
        - Flow entries for HTTP (TCP port 80), DNS (UDP port 53), and ICMP packets, that are forwarded to the controller with priority 10.

        Args:
            ev (EventOFPSwitchFeatures): The event representing the switch features.

        Returns:
            None
        """
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

        # If the only rule present is the one for general traffic (priority=1), forward to the controller HTTP, DNS and ICMP packets
        
        match_tcp = parser.OFPMatch(
            eth_type=ether_types.ETH_TYPE_IP,
            ip_proto=0x06, # TCP so HTTP
            tcp_dst=80
        )
        self.add_flow(datapath, 10, match_tcp, actions)

        match_udp = parser.OFPMatch(
            eth_type=ether_types.ETH_TYPE_IP,
            ip_proto=0x11, # UDP so DNS
            udp_dst=53
        )
        self.add_flow(datapath, 10, match_udp, actions)

        match_icmp = parser.OFPMatch(
            eth_type=ether_types.ETH_TYPE_IP,
            ip_proto=0x01, # ICMP
        )
        self.add_flow(datapath, 10, match_icmp, actions)


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
        """
        Add a flow entry to the switch's flow table.

        Args:
            datapath (Datapath): The datapath of the switch.
            priority (int): The priority of the flow entry.
            match (OFPMatch): The match criteria for the flow entry.
            actions (list): The actions to apply for the flow entry.

        Returns:
            None
        """        
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # construct flow_mod message and send it.
        inst = [parser.OFPInstructionActions(ofproto.OFPIT_APPLY_ACTIONS, actions)]
        mod = parser.OFPFlowMod(
            datapath=datapath, priority=priority, match=match, instructions=inst
        )
        datapath.send_msg(mod)

    def _send_package(self, msg, datapath, in_port, actions):
        """
        Send an OpenFlow packet-out message to the switch.

        Args:
            msg (OFPMsg): The OpenFlow message.
            datapath (Datapath): The datapath of the switch.
            in_port (int): The input port.
            actions (list): The actions to apply.

        Returns:
            None
        """        
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

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        """
        Handle Packet-In events sent by switches to the controller.
        These events occur when a packet does not match any flow rule or is explicitly 
        transmitted to the controller. The function processes the packet, determining its type 
        (HTTP, DNS, ICMP, or normal traffic) and creates appropriate actions and flow rules.

        Args:
            ev (EventOFPPacketIn): The event containing the Packet-In message.

        Returns:
            None
        """
        global current_modes
        msg = ev.msg
        datapath = msg.datapath
        dpid = datapath.id
        in_port = msg.match['in_port']
        ofp_parser = datapath.ofproto_parser # contains the parser
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)
        # ip_pkt = pkt.get_protocol(ipv4.ipv4) # If we want to change and add IP as a service
        tcp_pkt = pkt.get_protocol(tcp.tcp)
        udp_pkt = pkt.get_protocol(udp.udp)
        icmp_pkt = pkt.get_protocol(icmp.icmp)

        src = eth.src # MAC source
        dst = eth.dst # MAC destination to create match rules

        ipv4_pkt = pkt.get_protocol(ipv4.ipv4)
        if ipv4_pkt is None: # Packets that not contains ipv4 layer will be dropped, need to check this
            return
        
        out_ports = []
        switch_map = None
        entries = None
        for slice in current_modes: # Check if the communication requested is in one of the active slices
            if out_ports:
                break
            if dpid in self.slice_to_port[slice]:
                switch_map = self.slice_to_port[slice].get(dpid, {})
                if src in switch_map:
                    entries = switch_map.get(src, [])
                    for entry in entries:
                        if dst in entry:
                            out_ports.append(entry[dst])


        actions =[]
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
            self.add_flow(datapath, 100, match, actions)
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
            self.add_flow(datapath, 100, match, actions)
            self._send_package(msg, datapath, in_port, actions)
        elif icmp_pkt:
            # ICMP traffic
            print("ICMP traffic")
            for out_port in out_ports:
                if QUEUE_ICMP in self.queue_exists[datapath.id].get(out_port, []):
                    actions.append(ofp_parser.OFPActionSetQueue(QUEUE_ICMP))
                actions.append(ofp_parser.OFPActionOutput(out_port))
            match = ofp_parser.OFPMatch(
                in_port=in_port,
                eth_dst=dst,
                eth_type=ether_types.ETH_TYPE_IP,
                ip_proto=0x01,
            )
            self.add_flow(datapath, 100, match, actions)
            self._send_package(msg, datapath, in_port, actions)
        else:
            print("General traffic")
            for out_port in out_ports:
                if QUEUE_ICMP in self.queue_exists[datapath.id].get(out_port, []):
                    actions.append(ofp_parser.OFPActionSetQueue(QUEUE_GT))
                actions.append(ofp_parser.OFPActionOutput(out_port))
            match = datapath.ofproto_parser.OFPMatch(
                in_port=in_port,
                eth_dst=dst,
                eth_type=ether_types.ETH_TYPE_IP,
            )
            self.add_flow(datapath, 1, match, actions)
            self._send_package(msg, datapath, in_port, actions)

class SecondSlicingController(ControllerBase):
    """
    Controller API for managing network slicing modes.
    """
    index_to_mode_name = {
        0: "first_mode",
        1: "second_mode",
        2: "third_mode"
    }
    mode_name_to_index = {
        "first_mode": 0,
        "second_mode": 1,
        "third_mode": 2
    }

    def __init__(self, req, link, data, **config):
        super(SecondSlicingController, self).__init__(req, link, data, **config)
        self.second_slicing = data[second_slicing_instance_name]

    @staticmethod
    def get_cors_headers():
        """
        Get CORS headers.

        Args: None

        Returns:dict: A dictionary containing CORS headers.
        """
        return {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Content-Type': 'application/json'
        }

    def clear_flow_tables(self):
        """
        Clear all flow tables of the switches and reapply default flow rules.

        Args: None

        Returns: None
        """
        # Remove all flows tables
        for dp_i in self.second_slicing.datapaths:
            switch_dp = self.second_slicing.datapaths[dp_i]
            ofp_parser = switch_dp.ofproto_parser
            ofp = switch_dp.ofproto
            mod = ofp_parser.OFPFlowMod(
                datapath=switch_dp,
                table_id=ofp.OFPTT_ALL,
                command=ofp.OFPFC_DELETE,
                out_port=ofp.OFPP_ANY,
                out_group=ofp.OFPG_ANY
            )
            switch_dp.send_msg(mod)

        # Reinstall flow tables to avoid losing connectivity
        for dp_i in self.second_slicing.datapaths:
            datapath = self.second_slicing.datapaths[dp_i]
            parser = switch_dp.ofproto_parser
            ofp = switch_dp.ofproto
            match = ofp_parser.OFPMatch()
            actions = [
                ofp_parser.OFPActionOutput(ofp.OFPP_CONTROLLER, ofp.OFPCML_NO_BUFFER)
            ]
            self.second_slicing.add_flow(datapath, 0, match, actions)

             # If the only rule present is the one for general traffic (priority=1), forward to the controller HTTP, DNS and ICMP packets
        
            match_tcp = parser.OFPMatch(
                eth_type=ether_types.ETH_TYPE_IP,
                ip_proto=0x06, # TCP so HTTP
                tcp_dst=80

            )
            self.second_slicing.add_flow(datapath, 10, match_tcp, actions)

            match_udp = parser.OFPMatch(
                eth_type=ether_types.ETH_TYPE_IP,
                ip_proto=0x11, # UDP so DNS
                udp_dst=53
            )
            self.second_slicing.add_flow(datapath, 10, match_udp, actions)

            match_icmp = parser.OFPMatch(
                eth_type=ether_types.ETH_TYPE_IP,
                ip_proto=0x01, # ICMP
            )
            self.second_slicing.add_flow(datapath, 10, match_icmp, actions)

    def get_active_modes(self):
        """
        Get the current active mode.

        Args: None

        Returns: None
        """
        global current_modes
        modes = [self.index_to_mode_name[mode_index] for mode_index in sorted(current_modes)]
        modes = ", ".join(modes)
        return modes

    def set_mode(self, mode_name):
        """
        Toggle the specified mode in the current modes list.

        Args:
            mode_name (str): The mode to set (e.g., "first_mode", "second_mode", "third_mode").
    
        Returns: None
        """
        global current_modes
        mode_value = self.mode_name_to_index[mode_name]
        if mode_value in current_modes:
            current_modes.remove(mode_value)
        else:
            current_modes.append(mode_value)
        self.clear_flow_tables()

    @route("active_modes", url + "/active_modes", methods=["GET"])
    def fetch_active_modes(self, req, **kwargs):
        """
        Return the list of active modes.

        Args:
            req: The request object.
            **kwargs: Additional parameters.

        Returns:
            Response: A response containing the list of active modes as a string.
        """
        headers = self.get_cors_headers()
        global current_modes
        modes = [str(mode) for mode in current_modes]
        modes = ", ".join(modes)
        if not modes:
            modes = "No active modes"
        return Response(status=200, body=modes, headers=headers)

    @route("first_mode", url + "/first_mode", methods=["GET"])
    def toggle_first_mode(self, req, **kwargs):
        """
        Toggle the first mode.

        Args:
            req: The request object.
            **kwargs: Additional parameters.

        Returns:
            Response: A response containing the updated active modes.
        """
        headers = self.get_cors_headers()
        self.set_mode("first_mode")
        return Response(status=200, body=self.get_active_modes(), headers=headers)

    @route("second_mode", url + "/second_mode", methods=["GET"])
    def toggle_second_mode(self, req, **kwargs):
        """
        Toggle the second mode.

        Args:
            req: The request object.
            **kwargs: Additional parameters.

        Returns:
            Response: A response containing the updated active modes.
        """
        headers = self.get_cors_headers()
        self.set_mode("second_mode")
        return Response(status=200, body=self.get_active_modes(), headers=headers)

    @route("third_mode", url + "/third_mode", methods=["GET"])
    def toggle_third_mode(self, req, **kwargs):
        """
        Toggle the third mode.

        Args:
            req: The request object.
            **kwargs: Additional parameters.

        Returns:
            Response: A response containing the updated active modes.
        """
        headers = self.get_cors_headers()
        self.set_mode("third_mode")
        return Response(status=200, body=self.get_active_modes(), headers=headers)

    @route("qos", url + "/qos", methods=["POST", "OPTIONS"])
    def set_qos(self, req, **kwargs):
        headers = self.get_cors_headers()

        if req.method == "OPTIONS":
            return Response(status=200, headers=headers)

        data = json.loads(req.body.decode("utf-8"))
        values = data["values"]

        if len(values) != 3 or sum(values) > 10:
            return Response(status=400, body="The request must contain 3 values of total sum 10", headers=headers)

        values = [value * 1_000_000 for value in values] # convert the values into MBs
        values = [str(value) for value in values] # convert the values into strings to pass them as arguments

        qos = QoS()
        qos.start_process(*values)

        return Response(status=200, body="Values updated correctly" + str(values), headers=headers)
