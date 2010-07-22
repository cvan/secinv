from ConfigParser import ConfigParser
import sys

# Path to server configuration file.
SERVER_CONFIG_FN = 'server.conf'

# Parse server.conf for server settings and database credentials.
server_config = ConfigParser()

try:
    server_config.readfp(file(SERVER_CONFIG_FN))
except IOError:
    sys.exit("Error: Cannot open server configuration file '%s'"
             % SERVER_CONFIG_FN)

LISTEN_HOST = server_config.get('server', 'listen_host')
LISTEN_PORT = server_config.get('server', 'listen_port')

KEY_FILE = server_config.get('server', 'key_file')
CERT_FILE = server_config.get('server', 'cert_file')


import BaseHTTPServer
import SimpleHTTPServer
import SimpleXMLRPCServer
import SocketServer
import os
import socket

from OpenSSL import SSL


class SecureXMLRPCServer(BaseHTTPServer.HTTPServer,
                         SimpleXMLRPCServer.SimpleXMLRPCDispatcher):
    def __init__(self, server_address, HandlerClass, logRequests=True):
        """Secure XML-RPC server based on SimpleXMLRPCServer, using HTTPS."""
        self.logRequests = logRequests

        try:
            SimpleXMLRPCServer.SimpleXMLRPCDispatcher.__init__(self)
        except TypeError:
            # An exception is raised in Python 2.5, as the __init__ method
            # instead accepts three arguments: self, allow_none, encoding.
            SimpleXMLRPCServer.SimpleXMLRPCDispatcher.__init__(self, False, None)

        SocketServer.BaseServer.__init__(self, server_address, HandlerClass)
        ctx = SSL.Context(SSL.SSLv23_METHOD)
        ctx.use_privatekey_file(KEY_FILE)
        ctx.use_certificate_file(CERT_FILE)
        self.socket = SSL.Connection(ctx, socket.socket(self.address_family,
                                                        self.socket_type))
        self.server_bind()
        self.server_activate()


class RequestHandler(SimpleXMLRPCServer.SimpleXMLRPCRequestHandler):
    """Secure XML-RPC request handler class."""
    def __init__(self, request, client_address, server):
        self.client_ip = client_address
        SimpleXMLRPCServer.SimpleXMLRPCRequestHandler.__init__(self, request,
            client_address, server)

    def setup(self):
        self.connection = self.request
        self.rfile = socket._fileobject(self.request, 'rb', self.rbufsize)
        self.wfile = socket._fileobject(self.request, 'wb', self.wbufsize)
        
    def do_POST(self):
        """
        Handles the HTTPS POST request.

        It was copied out from SimpleXMLRPCServer.py and modified to shutdown
        the socket cleanly.
        """
        try:
            # Get arguments.
            data = self.rfile.read(int(self.headers['content-length']))

            # In previous versions of SimpleXMLRPCServer, _dispatch
            # could be overridden in this class, instead of in
            # SimpleXMLRPCDispatcher. To maintain backwards compatibility,
            # check to see if a subclass implements _dispatch and dispatch
            # using that method if present.
            response = self.server._marshaled_dispatch(data,
                getattr(self, '_dispatch', None))
        except:
            # Internal error -- report as HTTP server error.
            self.send_response(500)
            self.end_headers()
        else:
            # Received a valid XML-RPC response.
            self.send_response(200)
            self.send_header('Content-type', 'text/xml')
            self.send_header('Content-length', str(len(response)))
            self.end_headers()
            self.wfile.write(response)

            # Shut down the connection.
            self.wfile.flush()
            self.connection.shutdown()


def process(HandlerClass=RequestHandler, ServerClass=SecureXMLRPCServer):
    """Process XML-RPC commands over HTTPS server."""

    from functions import ServerFunctions

    # Initialize server.
    server_address = (LISTEN_HOST, int(LISTEN_PORT))
    server = ServerClass(server_address, HandlerClass)

    # Register XML-RPC functions.
    server.register_instance(ServerFunctions())
    server.register_multicall_functions()

    on_host, on_port = server.socket.getsockname()
    print "Serving HTTPS on %s port %s" % (on_host, on_port)

    server.serve_forever()


if __name__ == '__main__':
    process()

