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
    
    ####    
    #### Ports definitions
    ####
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

    ####
    #### Participant definitions
    ####
    participant_A = SDXParticipant(id_ = "A", ports = [port_A])
    participant_B = SDXParticipant(id_ = "B", ports = [port_B])
    participant_C = SDXParticipant(id_ = "C", ports = [port_C])

    sdx = SDXConfig()
    sdx.add_participant(participant_A)
    sdx.add_participant(participant_B)
    sdx.add_participant(participant_C)

    ####
    #### Policies definition
    ####
    participant_A.policies = (
        (match(dstip=port_A.ip) & sdx.fwd(port_A)) +
        (match(dstip=port_C.ip) & sdx.fwd("B"))
    )

    participant_B.policies=(
        (match(dstip=port_C.ip) & modify(srcmac=port_B.mac, dstmac=port_C.mac) & sdx.fwd("C")) +
        (match(dstip=port_A.ip) & modify(srcmac=port_B.mac, dstmac=port_A.mac) & sdx.fwd("A"))
    )

    participant_C.policies=(
        (match(dstip=port_C.ip) & sdx.fwd(port_C)) +
        (match(dstip=port_A.ip) & sdx.fwd("B"))
    )
    
    return sdx_platform(sdx)