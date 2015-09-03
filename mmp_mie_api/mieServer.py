import importlib
import argparse
import sys
import os
from mupif import PyroUtil, JobManager as jb
import logging
logger = logging.getLogger()


# required firewall settings (on ubuntu):
# for computer running daemon (this script)
# sudo iptables -A INPUT -p tcp -d 0/0 -s 0/0 --dport 44361 -j ACCEPT
# for computer running a nameserver
# sudo iptables -A INPUT -p tcp -d 0/0 -s 0/0 --dport 9090 -j ACCEPT

parser = argparse.ArgumentParser(description='Start MMP-Mie server. ')
parser.add_argument("configFile",
                    help='Configuration filename (py format)',
                    type=str, default='config.json')


def main():
    # Parse arguments
    args = parser.parse_args()
    sys.path.append(os.getcwd())

    # Load config
    tConf = importlib.import_module(args.configFile)

    # locate nameserver
    ns = PyroUtil.connectNameServer(nshost=tConf.nshost,
                                    nsport=tConf.nsport,
                                    hkey=tConf.hkey)

    # Run a daemon for jobMamager on this machine
    daemon = PyroUtil.runDaemon(host=tConf.daemonHost,
                                port=tConf.jobManPort,
                                nathost=tConf.nathost,
                                natport=tConf.jobManNatport)
    # Run job manager on a serverdaemon, ns, appAPIClass, appName, portRange,
    # jobManWorkDir, serverConfigPath, serverConfigFile, jobMan2CmdPath,
    # maxJobs=1, jobMancmdCommPort=10000
    jobMan = jb.SimpleJobManager2(daemon, ns,
                                  appAPIClass=tConf.applicationClass,
                                  appName=tConf.jobManName,
                                  portRange=tConf.jobManPortsForJobs,
                                  jobManWorkDir=tConf.jobManWorkDir,
                                  serverConfigPath=tConf.serverConfigPath,
                                  serverConfigFile=args.configFile,
                                  jobMan2CmdPath=tConf.jobMan2CmdPath,
                                  maxJobs=tConf.jobManMaxJobs,
                                  jobMancmdCommPort=tConf.jobManSocket)

    # set up daemon with JobManager
    uri = daemon.register(jobMan)
    # register JobManager to nameServer
    ns.register(tConf.jobManName, uri)
    logger.debug("Daemon for JobManager runs at " + str(uri))
    print(80 * '-')
    print("Started " + tConf.jobManName)
    # waits for requests
    daemon.requestLoop()


if __name__ == '__main__':
    main()