from ryu.base import app_manager
from ryu.controller import ofp_event
from ryu.controller.handler import CONFIG_DISPATCHER, MAIN_DISPATCHER
from ryu.controller.handler import set_ev_cls
from ryu.ofproto import ofproto_v1_3
from utility import get_mac_dict
from ryu.lib.packet import packet
from ryu.lib.packet import ethernet
from ryu.app.wsgi import ControllerBase, WSGIApplication, route
from webob import Response
import json

second_slicing_instance_name = "second_slicing_api_app"
url = "/controller/second"

class SecondSlicing(app_manager.RyuApp):
    OFP_VERSIONS = [ofproto_v1_3.OFP_VERSION]

    _CONTEXTS = {"wsgi": WSGIApplication}

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
            1: { 1: [3], 3: [1] },
            2: { 4: [5], 5: [4] },
            3: { 1: [2,3], 2: [1,3], 3: [1,2] }
        }
        #print("First configuration loaded:", self.slice_to_port)

        wsgi = kwargs["wsgi"]
        wsgi.register(SecondSlicingController, {second_slicing_instance_name: self})

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
        msg = ev.msg # contains the packet
        datapath = msg.datapath # contains the switch
        ofp_parser = datapath.ofproto_parser # contains the parser
        in_port = msg.match["in_port"]
        dpid = datapath.id

        out_ports = self.slice_to_port.get(dpid, {}).get(in_port, [])
        actions = []
        if out_ports is not None:
            for out_port in out_ports:
                actions.append(ofp_parser.OFPActionOutput(out_port))
            match = datapath.ofproto_parser.OFPMatch(in_port=in_port)
            self.add_flow(datapath, 1, match, actions) # add flow entry to the switch
            self._send_package(msg, datapath, in_port, actions)

class SecondSlicingController(ControllerBase):
    first_mode = 0
    second_mode = 0
    third_mode = 0
    first_qos = 0
    second_qos = 0
    third_qos = 0

    def __init__(self, req, link, data, **config):
        super(SecondSlicingController, self).__init__(req, link, data, **config)
        self.second_slicing = data[second_slicing_instance_name]

    @staticmethod
    def get_cors_headers():
        return {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST, OPTIONS',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Content-Type': 'application/json'
        }

    @staticmethod
    def get_active_modes():
        modes = []
        if SecondSlicingController.first_mode == 1:
            modes.append("First")
        if SecondSlicingController.second_mode == 1:
            modes.append("Second")
        if SecondSlicingController.third_mode == 1:
            modes.append("Third")
        modes = ", ".join(modes)
        return modes

    @route("first_mode", url + "/first_mode", methods=["GET"])
    def toggle_first_mode(self, req, **kwargs):
        headers = self.get_cors_headers()
        if SecondSlicingController.first_mode == 0:
            SecondSlicingController.first_mode = 1
        else:
            SecondSlicingController.first_mode = 0
        return Response(status=200, body=self.get_active_modes(), headers=headers)

    @route("second_mode", url + "/second_mode", methods=["GET"])
    def toggle_second_mode(self, req, **kwargs):
        headers = self.get_cors_headers()
        if SecondSlicingController.second_mode == 0:
            SecondSlicingController.second_mode = 1
        else:
            SecondSlicingController.second_mode = 0
        return Response(status=200, body=self.get_active_modes(), headers=headers)

    @route("third_mode", url + "/third_mode", methods=["GET"])
    def toggle_third_mode(self, req, **kwargs):
        headers = self.get_cors_headers()
        if SecondSlicingController.third_mode == 0:
            SecondSlicingController.third_mode = 1
        else:
            SecondSlicingController.third_mode = 0
        return Response(status=200, body=self.get_active_modes(), headers=headers)

    @route("qos", url + "/qos", methods=["POST", "OPTIONS"])
    def set_first_qos(self, req, **kwargs):
        headers = self.get_cors_headers()
        if req.method == "OPTIONS":
            return Response(status=200, headers=headers)

        data = json.loads(req.body.decode("utf-8"))
        values = data["values"]

        if len(values) != 3 or sum(values) != 10:
            return Response(status=400, body="The request must contain 3 values of total sum 10", headers=headers)

        SecondSlicingController.first_qos = values[0]
        SecondSlicingController.second_qos = values[1]
        SecondSlicingController.third_qos = values[2]

        return Response(status=200, body="Values updated correctly", headers=headers)
