import Pyro4

# Pyro configs
Pyro4.config.SERIALIZER = "pickle"
Pyro4.config.PICKLE_PROTOCOL_VERSION = 2  # to work with python 2.x and 3.x
Pyro4.config.SERIALIZERS_ACCEPTED = {'pickle'}

# Server config
server = '134.221.62.42'
serverPort = 44389
nshost = '134.221.62.42'  # NameServer - do not change
nsport = 19091  # NameServer's port - do not change
appName = "MMPMie@mmpserver"
hkey = ''  # Password for accessing nameServer and applications

hostUserName = 'mmpwp2test'  # User name for ssh connection
