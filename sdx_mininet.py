#!/usr/bin/python
"""
    Author: Arpit Gupta (glex.qsd@gmail.com)
    Author: Muhammad Shahbaz (firstname.lastname@gatech.edu)
    
    Steps:
    scp this script to VM running Mininet. 
    Make sure you have appropriate $PYTHONPATH
    Make sure your controller ip address is 192.168.56.1, else modify the controller_ip
        
"""

import sys, getopt
from mininet.topo import SingleSwitchTopo
from mininet.net import Mininet
from mininet.log import setLogLevel
from mininet.node import RemoteController
from mininet.cli import CLI

def getArgs():
    cli = False;
    controller = '127.0.0.1'    
    application = 'TO'
    
    try:
        opts, args = getopt.getopt(sys.argv[1:],"h",["help", "cli", "controller=", "application="])
    except getopt.GetoptError:
        print 'sdx_mininet.py [--cli --controller <ip address> --application <type>]'
        sys.exit(2)
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            
            print 'sdx_mininet.py [--cli --controller <ip address> --application <type>]'
            sys.exit()
        elif opt == '--cli':
            cli = True
        elif opt == '--controller':
            controller = arg
        elif opt == '--application':
            application = arg
    return (cli, controller, application)
   
def trafficOffloading(cli, controllerIP):
    "Create and test SDX Traffic Offloading Module"
    print "Creating the topology with one IXP switch and three participating ASs\n\n" 
    topo = SingleSwitchTopo(k=4)
    net = Mininet(topo, controller=lambda name: RemoteController( 'c0', controllerIP ), autoSetMacs=True, autoStaticArp=True)
    net.start()
    hosts=net.hosts
    print "Configuring participating ASs\n\n"
    for host in hosts:
        if host.name=='h1':
            host.cmd('ifconfig lo:40 110.0.0.1 netmask 255.255.255.0 up')
            host.cmd('route add -net 130.0.0.0 netmask 255.255.255.0 gw 10.0.0.2 h1-eth0')
            host.cmd('route add -net 140.0.0.0 netmask 255.255.255.0 gw 10.0.0.2 h1-eth0')
        if host.name=='h2':
            host.cmd('ifconfig lo:40 120.0.0.1 netmask 255.255.255.0 up')
        if host.name=='h3':
            host.cmd('ifconfig lo:40 130.0.0.1 netmask 255.255.255.0 up') 
            host.cmd('route add -net 110.0.0.0 netmask 255.255.255.0 gw 10.0.0.2 h3-eth0')
        if host.name=='h4':
            host.cmd('ifconfig lo:40 140.0.0.1 netmask 255.255.255.0 up')
            host.cmd('route add -net 110.0.0.0 netmask 255.255.255.0 gw 10.0.0.2 h4-eth0')
    if (cli): # Running CLI
        CLI(net)
    else:
        print "Running the Ping Tests\n\n"
        for host in hosts:
            if host.name=='h1':
                host.cmdPrint('ping -c 5 -I 110.0.0.1 130.0.0.1')
            elif host.name=='h3':
                    host.cmdPrint('ping -c 5 -I 130.0.0.1 110.0.0.1')
            elif host.name=='h1':
                host.cmdPrint('ping -c 5 -I 110.0.0.1 140.0.0.1')
            elif host.name=='h4':
                host.cmdPrint('ping -c 5 -I 140.0.0.1 110.0.0.1')

    net.stop()
    print "\n\nExperiment Complete !\n\n"

if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    # Parse arguments
    (cli, controller, application) = getArgs() 
    
    if (application == "TO"):
        trafficOffloading(cli, controller)   