################################################################################
# SDX: Software-Internet Exchange                                              #
# Author: Laurent Vanbever                                                     #
################################################################################

## Pyretic-specific imports
from pyretic.lib.corelib import *
from pyretic.lib.std import *

###
### SDX classes
###
class Port(object):
    """Represents a switch port"""
    def __init__(self, id_, mac, ip):
        self.id_ = id_
        self.mac = mac
        self.ip = ip

class SDXParticipant(object):
    """Represent a particular SDX participant"""
    def __init__(self, id_, ports, policies=None):
        self.id_ = id_
        self.ports = ports
        self.policies = policies

class SDXConfig(object):
    """Represent a SDX platform configuration"""
    def __init__(self):
        self.participants = []

        self.participant_id_to_in_var = {}        
        self.out_var_to_port = {}
        self.port_id_to_out_var = {}
    
    def add_participant(self, participant):
        self.participants.append(participant)
        self.participant_id_to_in_var[participant.id_] = "in" + participant.id_.upper()
        i = 0
        for port in participant.ports:
            self.port_id_to_out_var[port.id_] = "out" + participant.id_.upper() + "_" + str(i)
            self.out_var_to_port["out" + participant.id_.upper() + "_" + str(i)] = port
    
    def fwd(self, port):
        if isinstance(port, Port):
            return modify(state=self.port_id_to_out_var[port.id_])
        else:
            return modify(state=self.participant_id_to_in_var[port])
###
### SDX high-level functions
###
def sdx_restrict_state(sdx_config, participant):
    '''
        Prefix a match on the participant's state variable
        before any of the participant's policy to ensure that
        it cannot match on other participant's flowspace
    '''
    return match(state=sdx_config.participant_id_to_in_var[participant.id_]) & participant.policies

def sdx_preprocessing(sdx_config):
    '''
        Map incoming packets on participant's ports to the corresponding
        incoming state
    '''
    preprocessing_policies = []
    for participant in sdx_config.participants:
        for port in participant.ports:
            preprocessing_policies.append((match(inport=port.id_) & 
                modify(state=sdx_config.participant_id_to_in_var[participant.id_])))
    return parallel(preprocessing_policies)

def sdx_postprocessing(sdx_config):
    '''
        Forward outgoing packets to the appropriate participant's ports
        based on the outgoing state
    '''
    postprocessing_policies = []
    for output_var in sdx_config.out_var_to_port:
        postprocessing_policies.append((match(state=output_var) & pop("state") & 
            fwd(sdx_config.out_var_to_port[output_var].id_)))
    return parallel(postprocessing_policies)

def sdx_participant_policies(sdx_config):
    '''
        Sequentially compose the // composition of the participants policy k-times where
        k is the number of participants
    '''
    sdx_policy = passthrough
    for k in sdx_config.participants:
        sdx_policy = sequential([
                sdx_policy,
                parallel(
                    [sdx_restrict_state(sdx_config, participant) for participant in sdx_config.participants]
                )])
    return sdx_policy