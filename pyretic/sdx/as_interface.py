################################################################################
# SDX: Software-Internet Exchange                                              #
# Author: Arpit Gupta(glex.qsd@gmail.com)                                      #
################################################################################

import threading
import SocketServer
import logging as log
log.basicConfig(filename='sdx.log',level=log.INFO)

exchangeIP = "127.0.0.1"
exchangePort = 9006

class ThreadedTCPRequestHandler_exchange(SocketServer.BaseRequestHandler):

    def handle(self):
        log.info('Handler called')
        data = self.request.recv(1024)
        #print self.client_address[0]
        log.info('Received: %s',data)

        ## operations completed for this thread, send ok and let it go !
        response = 'ACK'
        self.request.sendall(response)

class ThreadedTCPServer(SocketServer.ThreadingMixIn, SocketServer.TCPServer):
    pass


class as_interface_thread(threading.Thread):
    def __init__(self,name):
        threading.Thread.__init__(self)
        self.name=name
    
    def run(self):
        log.info("AS interface thread started")
        HOST, PORT = exchangeIP, exchangePort
        server_exchange = ThreadedTCPServer((HOST, PORT), ThreadedTCPRequestHandler_exchange)
        ip, port = server_exchange.server_address
        server_thread_mc = threading.Thread(target=server_exchange.serve_forever)
        server_thread_mc.daemon = True
        server_thread_mc.start()
        log.info('Server running over IP:%s, port: %s',ip,port)

        # Keep server on until you get a keyboard interrupt "ctrl+c"
        try:
            server_exchange.serve_forever()
        except KeyboardInterrupt:
            pass
        finally:
            server_exchange.shutdown()
            log.info('Shutting down exchange server')
            log.info('bye')

