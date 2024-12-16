
from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from ryu.app.wsgi import ControllerBase, WSGIApplication, route
from webob import Response

first_slicing_instance_name = "first_slicing_api_app"
url = "/controller/first"

class TrafficSlicing(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    _CONTEXTS = {"wsgi": WSGIApplication}

    def __init__(self, *args, **kwargs):
        super(TrafficSlicing, self).__init__(*args, **kwargs)

        # out_port = slice_to_port[dpid][in_port]
        self.slice_to_port = { # Only connection beetween h6 (reception) and h9 (internet server)
            4: { 2: 1, 1: 2 }, # These numbers are the ports in which hosts/switches are connected, and the very first is the ID of the switch.
            1: { 3: 4, 4: 3 },
            5: { 1: 3, 3: 1 },
        }

        wsgi = kwargs["wsgi"]
        wsgi.register(FirstSlicingController, {first_slicing_instance_name: self})

    # COPIED FROM GRANELLI

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
        in_port = msg.match["in_port"]
        dpid = datapath.id
        out_port = self.slice_to_port.get(dpid, {}).get(in_port, None)
        print(in_port, dpid, out_port)

        if out_port is not None:
            actions = [datapath.ofproto_parser.OFPActionOutput(out_port)]
            match = datapath.ofproto_parser.OFPMatch(in_port=in_port)
            self.add_flow(datapath, 1, match, actions)
            self._send_package(msg, datapath, in_port, actions)

class FirstSlicingController(ControllerBase):
    mode_attributes = {
        "always_on_mode": 0,
        "listener_mode": 0,
        "no_guest_mode": 0,
        "speaker_mode": 0
    }

    def __init__(self, req, link, data, **config):
        super(FirstSlicingController, self).__init__(req, link, data, **config)
        self.first_slicing = data[first_slicing_instance_name]

    @staticmethod
    def get_cors_headers():
        return {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Content-Type': 'application/json'
        }

    def set_mode(self, mode_name):
        for mode in self.mode_attributes.keys():
            self.mode_attributes[mode] = 0
        self.mode_attributes[mode_name] = 1

    @route("always_on_mode", url + "/always_on_mode", methods=["GET"])
    def set_always_on_mode(self, req, **kwargs):
        headers = self.get_cors_headers()
        self.set_mode("always_on_mode")
        return Response(status=200, body="Current active mode: Always on", headers=headers)

    @route("listener_mode", url + "/listener_mode", methods=["GET"])
    def set_listener_mode(self, req, **kwargs):
        headers = self.get_cors_headers()
        self.set_mode("listener_mode")
        return Response(status=200, body="Current active mode: Listener", headers=headers)

    @route("no_guest_mode", url + "/no_guest_mode", methods=["GET"])
    def set_no_guest_mode(self, req, **kwargs):
        headers = self.get_cors_headers()
        self.set_mode("no_guest_mode")
        return Response(status=200, body="Current active mode: No guest", headers=headers)

    @route("speaker_mode", url + "/speaker_mode", methods=["GET"])
    def set_speaker_mode(self, req, **kwargs):
        headers = self.get_cors_headers()
        self.set_mode("speaker_mode")
        return Response(status=200, body="Current active mode: Speaker", headers=headers)
