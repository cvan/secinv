from ConfigParser import ConfigParser
from discovery import Assets, AssetsIP
import xmlrpclib

CLIENT_CONFIG_FN = 'inventory.conf'
client_config = ConfigParser()

try:
    client_config.readfp(file(CLIENT_CONFIG_FN))
except IOError:
    sys.exit("\n\tError: Cannot open inventory configuration file '%s'\n"
             % CLIENT_CONFIG_FN)


# TODO: Error checking. Check if we can connect.
proxy = xmlrpclib.ServerProxy("%s:%s" % (client_config.get('server', 'host'),
                                         client_config.get('server', 'port')))

multicall = xmlrpclib.MultiCall(proxy)

# Compare authentication keys.
multicall.authenticate(client_config.get('server', 'auth_key'))

# TODO: Check for baseline.

assets_ip = AssetsIP()
assets_ip_dict = getattr(assets_ip, 'get_interfaces')()

assets = Assets()
assets_dict = getattr(assets, 'get_assets_dict')()

multicall.assets_ip(assets_ip_dict)
multicall.assets(assets_dict)


result = multicall()

print "Authentication: %s\n\nReceived assets_ip info:  %s\n\nReceived assets info:  %s" % tuple(result)


print '\nassets_ip_dict:'
print assets_ip_dict

print '\nassets_dict:'
print assets_dict

print '\n'
