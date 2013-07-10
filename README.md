============
SDX Platform
============

Installation Steps
--------------

If you haven't already done so, download Pyretic v0.2.0
> $ wget http://frenetic-lang.org/pyretic/vms/pyretic_0.2.0.ova

In your Virtual Machine:

a. Update the copy of Mininet (this resolves the `--arp` issue) 
> $ cd ~/mininet; git pull --rebase; sudo make develop

b. Clone sdx-platform repository to your home directory
> $ cd ~   
> $ git clone https://github.com/sdn-ixp/sdx-platform.git

c. Setup your environment variables,
remove following lines from end of `~/.profile`:
> export PATH=$PATH:$HOME/pyretic:$HOME/pox   
> export PYTHONPATH=$HOME/pyretic:$HOME/mininet:$HOME/pox

and add the following lines, instead:
> export PATH=$PATH:$HOME/sdx-platform:$HOME/pox   
> export PYTHONPATH=$HOME/sdx-platform:$HOME/mininet:$HOME/pox

Running SDX Plaform
--------------

Execute `python pyretic.py pyretic.sdx.platform`. After this launch the Mininet experiment.

Launching the Mininet Experiment  
------------------------  

* Transfer the file `sdx_mininet.py` to your Mininet VM.  
* Run the command, `sudo python sdx_mininet.py`     

This Mininet script creates a single topology with three hosts. It does all the interface configurations, routing table updates etc. and finally runs two ping tests.  

If you face any problem with `sdx_mininet.py` script, then follow these steps manually:  

* Creating the topology with three ASs and one IXP switch:  
`sudo mn --controller=remote --topo=single,3 --mac --arp`

* Configuring the participating ASs in Mininet: 
`h1 ifconfig lo:40 110.0.0.1 netmask 255.255.255.0 up` 
`h2 ifconfig lo:40 120.0.0.1 netmask 255.255.255.0 up` 
`h3 ifconfig lo:40 130.0.0.1 netmask 255.255.255.0 up` 
`h4 ifconfig lo:40 140.0.0.1 netmask 255.255.255.0 up`

`h1 route add -net 130.0.0.0 netmask 255.255.255.0 gw 10.0.0.2 h1-eth0`
`h1 route add -net 140.0.0.0 netmask 255.255.255.0 gw 10.0.0.2 h1-eth0`
`h3 route add -net 110.0.0.0 netmask 255.255.255.0 gw 10.0.0.2 h3-eth0`
`h4 route add -net 110.0.0.0 netmask 255.255.255.0 gw 10.0.0.2 h4-eth0`

* Starting a ping with the appropriate source and destination mac addresses  
`h1 ping -I 110.0.0.1 130.0.0.1`
`h3 ping -I 130.0.0.1 110.0.0.1`

`h1 ping -I 110.0.0.1 140.0.0.1`
`h4 ping -I 140.0.0.1 110.0.0.1`

