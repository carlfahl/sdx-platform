################################################################################
# SDX: Software-Internet Exchange                                              #
# Author: Laurent Vanbever                                                     #
################################################################################

## Pyretic-specific imports
from pyretic.lib.corelib import *
from pyretic.lib.std import *

## SDX-specific imports
from config import *

## SDX functions
def sdx_restrict_state(participant):
    '''
        Prefix a match on the participant's state variable
        before any of the participant's policy to ensure that
        it cannot match on other participant's flowspace
    '''
    return match(state=participant.input_var) & participant.policies

def sdx_preprocessing():
    '''
        Map incoming packets on participant's ports to the corresponding
        incoming state
    '''
    preprocessing_policies = []
    for participant in sdx_config.participants:
        for port in participant.ports:
            preprocessing_policies.append((match(inport=port.id_) & modify(state=participant.input_var)))
    return parallel(preprocessing_policies)

def sdx_postprocessing():
    '''
        Forward outgoing packets to the appropriate participant's ports
        based on the outgoing state
    '''
    postprocessing_policies = []
    for participant in sdx_config.participants:
        for output_var in participant.output_vars:
            postprocessing_policies.append((match(state=output_var) & pop("state") & fwd(participant.output_vars[output_var].id_)))
    return parallel(postprocessing_policies)

def sdx_participant_policies():
    '''
        Sequentially compose the // composition of the participants policy k-times where
        k is the number of participants
    '''
    sdx_policy = passthrough
    for k in sdx_config.participants:
        sdx_policy = sequential([
                sdx_policy,
                parallel(
                    [sdx_restrict_state(participant) for participant in sdx_config.participants]
                )])
    return sdx_policy

def sdx_platform():
    '''
        Defines the SDX platform workflow
    '''
    return (
        sdx_preprocessing() >>
        sdx_participant_policies() >>
        sdx_postprocessing()
    )

### SDX Platform: Main ###
def main(): 
    return sdx_platform()