################################################################################
# SDX: Software-Internet Exchange                                              #
# Author: Laurent Vanbever                                                     #
################################################################################

## Pyretic-specific imports
from pyretic.lib.corelib import *
from pyretic.lib.std import *

class Port(object):
    """Represents a switch port"""
    def __init__(self, id_, mac, ip):
        super(Port, self).__init__()
        self.id_ = id_
        self.mac = mac
        self.ip = ip

class SDXParticipant(object):
    """Represent a particular SDX participant"""
    def __init__(self, id_, ports, input_var, output_vars, policies):
        self.id_ = id_
        self.ports = ports
        self.input_var = input_var
        self.output_vars = output_vars
        self.policies = policies

class SDXConfig(object):
    """Represent a SDX platform configuration"""
    def __init__(self):
        super(SDXConfig, self).__init__()
        self.participants = []
    
    def add_participant(self, participant):
        self.participants.append(participant)


#### Ports definitions
port_A = Port(
    id_ = 1, 
    mac = MAC('00:00:00:00:00:01'), 
    ip = IP('110.0.0.1')
)

port_B = Port(
    id_ = 2, 
    mac = MAC('00:00:00:00:00:02'), 
    ip = IP('120.0.0.1')
)

port_C = Port(
    id_ = 3, 
    mac = MAC('00:00:00:00:00:03'), 
    ip = IP('130.0.0.1')
)

#### Participant definitions
participant_A = SDXParticipant(
    id_ = "A",
    ports = [port_A],
    input_var = "inA",
    output_vars = {
        'outA' : port_A
    },
    policies = (
        (match(dstip=port_A.ip) & modify(state='outA')) +
        (match(dstip=port_C.ip) & modify(state='inB'))
    )
)

participant_B = SDXParticipant(
    id_ = "B",
    ports = [port_B],
    input_var = "inB",
    output_vars = {
        'outB' : port_B
    },
    policies = (
        (match(dstip=port_C.ip) & modify(srcmac=port_B.mac, dstmac=port_C.mac, state='inC')) +
        (match(dstip=port_A.ip) & modify(srcmac=port_B.mac, dstmac=port_A.mac, state='inA'))
    )
)

participant_C = SDXParticipant(
    id_ = "C",
    ports = [port_C],
    input_var = "inC",
    output_vars = {
        'outC' : port_C
    },
    policies = (
        (match(dstip=port_C.ip) & modify(state='outC')) +
        (match(dstip=port_A.ip) & modify(state='inB'))
    )
)

#### SDX Config definitions
sdx_config = SDXConfig()
sdx_config.add_participant(participant_A)
sdx_config.add_participant(participant_B)
sdx_config.add_participant(participant_C)