from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER, set_ev_cls, DEAD_DISPATCHER
from ryu.ofproto import ofproto_v1_3
from ryu.app.wsgi import ControllerBase, WSGIApplication, route
from ryu.lib.packet import packet, ethernet, ether_types, ipv4
from webob import Response
from enum import Enum

from utils import slice_to_port

class FirstTopologyModes(Enum):
    ALWAYS_ON = 0
    NO_GUEST = 1
    LISTENER = 2
    SPEAKER = 3

current_mode = FirstTopologyModes.NO_GUEST

first_slicing_instance_name = "first_slicing_api_app"
url = "/controller/first"

class FirstSlicing(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    _CONTEXTS = {"wsgi": WSGIApplication}

    def __init__(self, *args, **kwargs):
        super(FirstSlicing, self).__init__(*args, **kwargs)

        self.datapaths = {}
        self.slice_to_port = slice_to_port()

        wsgi = kwargs["wsgi"]
        wsgi.register(FirstSlicingController, {first_slicing_instance_name: self})

    def update_slice(self, mode):
        self.slice_to_port = slice_to_port(mode.value)
        print(f"Slice changed to {mode}!")

        # Remove all flows tables
        for dp_i in self.datapaths:
            switch_dp = self.datapaths[dp_i]
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
        for dp_i in self.datapaths:
            switch_dp = self.datapaths[dp_i]
            ofp_parser = switch_dp.ofproto_parser
            ofp = switch_dp.ofproto
            match = ofp_parser.OFPMatch() 
            actions = [
                ofp_parser.OFPActionOutput(ofp.OFPP_CONTROLLER, ofp.OFPCML_NO_BUFFER)
            ]
            self.add_flow(switch_dp, 0, match, actions)
        
    @set_ev_cls(ofp_event.EventOFPStateChange, [MAIN_DISPATCHER, DEAD_DISPATCHER])
    def _state_change_handler(self, ev):
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
        datapath = ev.msg.datapath
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

        # install the table-miss flow entry.
        match = parser.OFPMatch()
        actions = [
            parser.OFPActionOutput(ofproto.OFPP_CONTROLLER, ofproto.OFPCML_NO_BUFFER)
        ]
        self.add_flow(datapath, 0, match, actions)

    def add_flow(self, datapath, priority, match, actions):
        ofproto = datapath.ofproto
        parser = datapath.ofproto_parser

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

    @set_ev_cls(ofp_event.EventOFPPacketIn, MAIN_DISPATCHER)
    def _packet_in_handler(self, ev):
        msg = ev.msg
        datapath = msg.datapath
        in_port = msg.match["in_port"]
        dpid = datapath.id
        pkt = packet.Packet(msg.data)
        eth = pkt.get_protocol(ethernet.ethernet)

        if eth.ethertype == ether_types.ETH_TYPE_LLDP:
            # Ignore LLDP packets
            return

        ipv4_pkt = pkt.get_protocol(ipv4.ipv4)
        if ipv4_pkt is None:
            return

        src_ip = ipv4_pkt.src
        dst_ip = ipv4_pkt.dst

        out_port = None
        for entry in self.slice_to_port.get(dpid, {}).get(src_ip, []):
            if dst_ip in entry:
                out_port = entry[dst_ip]
                break

        print(f"Packet In - In Port: {in_port}, DPID: {dpid}, Out Port: {out_port}, Src IP: {src_ip}, Dst IP: {dst_ip}")

        if out_port is not None:
            actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
            match = datapath.ofproto_parser.OFPMatch(
                in_port=in_port,
                eth_type=ether_types.ETH_TYPE_IP,
                ipv4_src=src_ip,
                ipv4_dst=dst_ip,
            )
            self.add_flow(datapath, 1, match, actions)
            self._send_package(msg, datapath, in_port, actions)

class FirstSlicingController(ControllerBase):
    def __init__(self, req, link, data, **config):
        super(FirstSlicingController, self).__init__(req, link, data, **config)
        self.first_slicing = data[first_slicing_instance_name]

    @staticmethod
    def get_cors_headers():
        return {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
            "Access-Control-Allow-Headers": "Content-Type",
            "Content-Type": "application/json",
        }

    @route("always_on_mode", url + "/always_on_mode", methods=["GET"])
    def set_always_on_mode(self, req, **kwargs):
        global current_mode
        headers = self.get_cors_headers()
        current_mode = FirstTopologyModes.ALWAYS_ON
        self.first_slicing.update_slice_to_port(current_mode)
        return Response(status=200, body="Current active mode: Always on", headers=headers)

    @route("listener_mode", url + "/listener_mode", methods=["GET"])
    def set_listener_mode(self, req, **kwargs):
        global current_mode
        headers = self.get_cors_headers()
        current_mode = FirstTopologyModes.LISTENER
        self.first_slicing.update_slice(current_mode)
        return Response(status=200, body="Current active mode: Listener", headers=headers)

    @route("no_guest_mode", url + "/no_guest_mode", methods=["GET"])
    def set_no_guest_mode(self, req, **kwargs):
        global current_mode
        headers = self.get_cors_headers()
        current_mode = FirstTopologyModes.NO_GUEST
        self.first_slicing.update_slice(current_mode)
        return Response(status=200, body="Current active mode: No guest", headers=headers)

    @route("speaker_mode", url + "/speaker_mode", methods=["GET"])
    def set_speaker_mode(self, req, **kwargs):
        global current_mode
        headers = self.get_cors_headers()
        current_mode = FirstTopologyModes.SPEAKER
        self.first_slicing.update_slice(current_mode)
        return Response(status=200, body="Current active mode: Speaker", headers=headers)
