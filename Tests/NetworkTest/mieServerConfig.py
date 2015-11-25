import Pyro4

# Pyro configs
Pyro4.config.SERIALIZER = "pickle"
Pyro4.config.PICKLE_PROTOCOL_VERSION = 2  # to work with python 2.x and 3.x
Pyro4.config.SERIALIZERS_ACCEPTED = {'pickle'}

# Server config
server = 'mmpserver.erve.vtt.fi'
serverPort = 9102
serverNathost = 'localhost'
serverNatport = 5555

# Namesercer
nshost = 'mech.FSV.CVUT.CZ'  # NameServer - do not change
nsport = 9090  # NameServer's port - do not change
# Application id and key
appName = "MMPMie@mmpserver"
hkey = 'mmp-secret-key'  # Password for accessing nameServer and applications
