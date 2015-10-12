import os
from mmp_mie_api import MMPMie
import socket
import Pyro4
Pyro4.config.SERIALIZER = "pickle"
Pyro4.config.PICKLE_PROTOCOL_VERSION = 2  # to work with python 2.x and 3.x
Pyro4.config.SERIALIZERS_ACCEPTED = {'pickle'}
Pyro4.config.HOST = 'mmpserver.erve.vtt.fi'

serverConfigPath = os.getcwd()

nshost = 'mech.FSV.CVUT.CZ'  # NameServer - do not change
nsport = 9090  # NameServer's port - do not change
hkey = 'mmp-secret-key'  # Password for accessing nameServer and applications
nathost = 'localhost'  # NatHost of local computer - do not change
serverNathost = 'localhost'  # NatHost of local computer - do not change

server = 'mmpserver.erve.vtt.fi'
daemonHost = 'mmpserver.erve.vtt.fi'  # IP of server
hostUserName = 'otolli'  # User name for ssh connection

jobManPort = 44360  # Port for job manager's daemon
jobManNatport = 5557  # Natport - nat port used in ssh tunnel for job manager
jobManSocket = 10000  # Port used to communicate with application servers

jobManName = 'Mupif.JobManager@MMPMie'
applicationClass = MMPMie

# Range of ports to be assigned on the server to jobs
jobManPortsForJobs = (9095, 9140)
jobManMaxJobs = 40  # Maximum number of jobs
# Main directory for transmitting files
jobManWorkDir = os.path.abspath(os.path.join(os.getcwd(), 'mieWorkDir'))

applicationClass = MMPMie

# path to JobMan2cmd.py
jobMan2CmdPath = "jobMan2cmd"
