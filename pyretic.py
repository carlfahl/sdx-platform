#!/usr/bin/python

################################################################################
# The Pyretic Project                                                          #
# frenetic-lang.org/pyretic                                                    #
# author: Joshua Reich (jreich@cs.princeton.edu)                               #
################################################################################
# Licensed to the Pyretic Project by one or more contributors. See the         #
# NOTICES file distributed with this work for additional information           #
# regarding copyright and ownership. The Pyretic Project licenses this         #
# file to you under the following license.                                     #
#                                                                              #
# Redistribution and use in source and binary forms, with or without           #
# modification, are permitted provided the following conditions are met:       #
# - Redistributions of source code must retain the above copyright             #
#   notice, this list of conditions and the following disclaimer.              #
# - Redistributions in binary form must reproduce the above copyright          #
#   notice, this list of conditions and the following disclaimer in            #
#   the documentation or other materials provided with the distribution.       #
# - The names of the copyright holds and contributors may not be used to       #
#   endorse or promote products derived from this work without specific        #
#   prior written permission.                                                  #
#                                                                              #
# Unless required by applicable law or agreed to in writing, software          #
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT    #
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the     #
# LICENSE file distributed with this work for specific language governing      #
# permissions and limitations under the License.                               #
################################################################################

from pyretic.core.runtime import Runtime
from pyretic.backend.backend import Backend
import sys
import threading
import signal
import subprocess
from importlib import import_module
from optparse import OptionParser
import re
import os

of_client = None

def signal_handler(signal, frame):
    print '\n----starting pyretic shutdown------'
#    for thread in threading.enumerate():
#        print (thread,thread.isAlive())
    print "attempting to kill of_client"
    of_client.kill()
    print "attempting get output of of_client:"
    output = of_client.communicate()[0]
    print output
    print "pyretic.py done"
    sys.exit(0)


def parseArgs():
    """Parse command-line args and return options object.
    returns: opts parse options dict"""
    desc = ( 'Pyretic runtime' )
    usage = ( '%prog [options]\n'
              '(type %prog -h for details)' )
    
    end_args = 0
    for arg in sys.argv[1:]:
        if not re.match('-',arg):
            end_args = sys.argv.index(arg)
    kwargs_to_pass = None
    if end_args > 0:
        kwargs_to_pass = sys.argv[end_args+1:]
        sys.argv = sys.argv[:end_args+1]

    op = OptionParser( description=desc, usage=usage )
    op.add_option( '--frontend-only', '-f', action="store_true", 
                     dest="frontend_only", help = 'only start the frontend'  )
    op.add_option( '--mode', '-m', type='choice',
                     choices=['interpreted','i','reactive0','r0'], 
                     help = '|'.join( ['interpreted/i','reactive0/r0'] )  )
    op.add_option( '--verbosity', '-v', type='choice',
                     choices=['low','normal','high'], default = 'low',
                     help = '|'.join( ['quiet','high'] )  )

    op.set_defaults(frontend_only=False,mode='reactive0')
    options, args = op.parse_args()

    return (op, options, args, kwargs_to_pass)


def main():
    global of_client
    (op, options, args, kwargs_to_pass) = parseArgs()
    if options.mode == 'i':
        options.mode = 'interpreted'
    elif options.mode == 'r0':
        options.mode = 'reactive0'
    try:
        module_name = args[0]
    except IndexError:
        print 'Module must be specified'
        print ''
        op.print_usage()
        sys.exit(1)
    try:
        module = import_module(module_name)
    except ImportError:
        print 'Must be a valid python module'
        print 'e.g, full module name,'
        print '     no .py suffix,'
        print '     located on the system PYTHONPATH'
        print ''
        op.print_usage()
        sys.exit(1)
    print "Initial things work fine "
    main = module.main
    kwargs = { k : v for [k,v] in [ i.lstrip('--').split('=') for i in kwargs_to_pass ]}

    sys.setrecursionlimit(1500) #INCREASE THIS IF "maximum recursion depth exceeded"
    
    runtime = Runtime(Backend(),main,kwargs,options.mode,options.verbosity,False,False)
    print "Runtime works fine"
    if not options.frontend_only:
        try:
            output = subprocess.check_output('echo $PYTHONPATH',shell=True).strip()
        except:
            print 'Error: Unable to obtain PYTHONPATH'
            sys.exit(1)
        poxpath = None
        print "find pox path "
        for p in output.split(':'):
             if re.match('.*pox/?$',p):
                 poxpath = os.path.abspath(p)
                 break
        if poxpath is None:
            print 'Error: pox not found in PYTHONPATH'
            sys.exit(1)
        print "found pox path "+str(poxpath)
        pox_exec = os.path.join(poxpath,'pox.py')
        python=sys.executable
        of_client = subprocess.Popen([python, 
                                      pox_exec,
                                      'of_client.pox_client' ],
                                     stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
   	print of_client 
    signal.signal(signal.SIGINT, signal_handler)
    signal.pause()

if __name__ == '__main__':
    main()
