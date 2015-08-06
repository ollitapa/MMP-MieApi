import sys
sys.path.append('/home/mmp/mupif-code')

#import demoapp
from mmp_mie_api import MMPMie

import Pyro4
Pyro4.config.SERIALIZER="pickle"
Pyro4.config.PICKLE_PROTOCOL_VERSION=2 #to work with python 2.x and 3.x
Pyro4.config.SERIALIZERS_ACCEPTED={'pickle'}
hkey = 'mmp-secret-key'

nshost = '147.32.130.137' #NameServer - do not change
nsport  = 9090 #NameServer's port - do not change
hkey = 'mmp-secret-key' #Password for accessing nameServer and applications
nathost='127.0.0.1' #NatHost of local computer - do not change

daemonHost='127.0.1.1'#'147.32.130.137'#IP of server
hostUserName='mmp'#User name for ssh connection

jobManPort=44360#Port for job manager's daemon
jobManNatport=5555 #Natport - nat port used in ssh tunnel for job manager
jobManSocket=10000 #Port used to communicate with application servers
#jobManName='Mupif.JobManager@ThermalSolverDemo' #Name of job manager
jobManName = 'Mupif.JobManager@MMPMie'

jobManPortsForJobs=( 9095, 9100) #Range of ports to be assigned on the server to jobs
jobManMaxJobs=4 #Maximum number of jobs
jobManWorkDir='/home/elemim/GITHUB/MMP-TracerApi/Tests/work/mieWorkDir'#'/home/mmp/work/thermalWorkDir'#Main directory for transmitting files

applicationClass = MMPMie #demoapp.thermal
jobMan2CmdPath = '/home/elemim/mupif/mupif-code/mupif/tools/JobMan2cmd.py' #"../../tools/JobMan2cmd.py" # path to JobMan2cmd.py 

