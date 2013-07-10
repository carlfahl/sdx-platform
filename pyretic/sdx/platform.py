################################################################################
# SDX: Software-Internet Exchange                                              #
# Author: Laurent Vanbever                                                     #
################################################################################

## Pyretic-specific imports
from pyretic.lib.corelib import *
from pyretic.lib.std import *

## SDX-specific imports
from core import *

def sdx_platform(sdx_config):
    '''
        Defines the SDX platform workflow
    '''
    return (
        sdx_preprocessing(sdx_config) >>
        sdx_participant_policies(sdx_config) >>
        sdx_postprocessing(sdx_config)
    )

### SDX Platform: Main ###
def main():
    
    ip_A  = IP('110.0.0.1')
    ip_B  = IP('120.0.0.1')
    ip_C1 = IP('130.0.0.1')
    ip_C2 = IP('140.0.0.1')
    
    ####    
    #### PhysicalPort definitions
    ####
    port_A = PhysicalPort(id_ = 1, mac = MAC('00:00:00:00:00:01'))
    port_B = PhysicalPort(id_ = 2, mac = MAC('00:00:00:00:00:02'))
    port_C1 = PhysicalPort(id_ = 3, mac = MAC('00:00:00:00:00:03'))
    port_C2 = PhysicalPort(id_ = 4, mac = MAC('00:00:00:00:00:04'))
    
    ####    
    #### VirtualPorts definitions
    ####
    vport_A = VirtualPort(mac = port_A.mac)
    vport_B = VirtualPort(mac = port_B.mac)
    vport_C = VirtualPort(mac = port_C1.mac)

    ####
    #### Participant definitions
    ####
    participant_A = SDXParticipant(id_ = "A", vport=vport_A, phys_ports = [port_A])
    participant_B = SDXParticipant(id_ = "B", vport=vport_B, phys_ports = [port_B])
    participant_C = SDXParticipant(id_ = "C", vport=vport_C, phys_ports = [port_C1, port_C2])

    sdx = SDXConfig()
    sdx.add_participant(participant_A)
    sdx.add_participant(participant_B)
    sdx.add_participant(participant_C)

    ####
    #### Policies definition
    ####
    participant_A.policies = (
        if_(sdx_from(vport_C) , drop) >> (
            (match(dstip=ip_A)  & sdx.fwd(port_A)) +
            (match(dstip=ip_C1) & sdx.fwd(vport_B)) +
            (match(dstip=ip_C2) & sdx.fwd(vport_B))
        )
    )

    participant_B.policies=(
        (match(dstip=ip_C1) & modify(srcmac=vport_B.mac, dstmac=vport_C.mac) & sdx.fwd(vport_C)) +
        (match(dstip=ip_C2) & modify(srcmac=vport_B.mac, dstmac=vport_C.mac) & sdx.fwd(vport_C)) +
        (match(dstip=ip_A)  & modify(srcmac=vport_B.mac, dstmac=vport_A.mac) & sdx.fwd(vport_A))
    )

    participant_C.policies=(
        (match(dstip=ip_C1) & sdx.fwd(port_C1)) +
        (match(dstip=ip_C2) & sdx.fwd(port_C2)) +
        (match(dstip=ip_A)  & sdx.fwd(vport_B))
    )
    
    return sdx_platform(sdx)
