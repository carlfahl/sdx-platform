#!/usr/bin/python
"""
    Author: Arpit Gupta (glex.qsd@gmail.com)
    scp this script to VM running Mininet. 
    Make sure you have appropriate $PYTHONPATH
    Make sure your controller ip address is 192.168.56.1, else modify the controller_ip
        
"""


from mininet.topo import Topo
from mininet.net import Mininet
from mininet.util import dumpNodeConnections
from mininet.log import setLogLevel
from mininet.node import Controller, RemoteController



controller_ip='192.168.56.1'


class SDXSwitchTopo(Topo):
    "SDX: Single switch connected to n hosts."
    def __init__(self, n=2, **opts):
        # Initialize topology and default options
        Topo.__init__(self, **opts)
        switch = self.addSwitch('s1')
        # Python's range(N) generates 0..N-1
        for h in range(n):
            host = self.addHost('h%s' % (h + 1))
            self.addLink(host, switch)

def Traffic_Offloading():
    "Create and test SDX Traffic Offloading Module"
    print "Creating the topology with one IXP switch and three participating ASs\n\n" 
    topo = SDXSwitchTopo(n=4)
    c0 = RemoteController( 'c0', ip=controller_ip )
    net = Mininet(topo, autoSetMacs=True, autoStaticArp=True)
    net.controllers=[c0]
    net.start()
    hosts=net.hosts
    #print hosts
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
    
    print "Running the Ping Tests\n\n"
    for host in hosts:
        if host.name=='h1':
            host.cmdPrint('ping -c 5 -I 110.0.0.1 130.0.0.1')
        if host.name=='h3':
            host.cmdPrint('ping -c 5 -I 130.0.0.1 110.0.0.1')
        if host.name=='h1':
            host.cmdPrint('ping -c 5 -I 110.0.0.1 140.0.0.1')
    net.stop()
    print "\n\nExperiment Complete !\n\n"

if __name__ == '__main__':
    # Tell mininet to print useful information
    setLogLevel('info')
    # Currently we are running mininet to test traffic offloading module for SDX
    # Infuture we can write various other test modules 
    Traffic_Offloading()
