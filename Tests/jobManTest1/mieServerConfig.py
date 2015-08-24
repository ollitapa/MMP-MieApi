import mupif
import os

#import demoapp
from mmp_mie_api import MMPMie

import Pyro4
Pyro4.config.SERIALIZER = "pickle"
Pyro4.config.PICKLE_PROTOCOL_VERSION = 2  # to work with python 2.x and 3.x
Pyro4.config.SERIALIZERS_ACCEPTED = {'pickle'}
hkey = 'mmp-secret-key'

serverConfigPath = os.getcwd()

nshost = '147.32.130.137'  # NameServer - do not change
nsport = 9090  # NameServer's port - do not change
hkey = 'mmp-secret-key'  # Password for accessing nameServer and applications
nathost = 'localhost'  # NatHost of local computer - do not change

daemonHost = 'localhost'  # '147.32.130.137'#IP of server
hostUserName = 'mmp'  # User name for ssh connection

jobManPort = 44360  # Port for job manager's daemon
jobManNatport = 5555  # Natport - nat port used in ssh tunnel for job manager
jobManSocket = 10000  # Port used to communicate with application servers
# jobManName='Mupif.JobManager@ThermalSolverDemo' #Name of job manager
jobManName = 'Mupif.JobManager@MMPMie'

# Range of ports to be assigned on the server to jobs
jobManPortsForJobs = (9095, 9100)
jobManMaxJobs = 4  # Maximum number of jobs
# '/home/mmp/work/thermalWorkDir'#Main directory for transmitting files
jobManWorkDir = os.path.abspath(os.path.join(os.getcwd(), 'mieWorkDir'))

applicationClass = MMPMie  # demoapp.thermal
# "../../tools/JobMan2cmd.py" # path to JobMan2cmd.py
jobMan2CmdPath = os.path.join(os.path.dirname(mupif.__file__),
                              'tools', 'JobMan2cmd.py')
