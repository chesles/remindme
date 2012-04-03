#!/usr/bin/python


import sys
import os
from socket import gethostname
from grizzled.os import daemonize



PYTHON_BINARY = "python"
PATH_TO_PYTHON_BINARY = "/usr/bin/%s" % PYTHON_BINARY
ROTATELOGS_CMD = "/usr/sbin/rotatelogs"
LOGDIR = "/opt/tornado/logs"
LOGDURATION = 86400

logdir = LOGDIR
logger = ROTATELOGS_CMD
hostname = gethostname()
# service is the name of the Python module pointing to your Tornado web server
# for example myapp.web
execve_args = [PYTHON_BINARY]
execve_args.extend(sys.argv[1:])

service = sys.argv[1].split('/')[-1]

logfile = "%s_%s_log.%%Y-%%m-%%d" % (service, hostname)
pidfile = "%s/%s.pid" % (logdir, service)
logpipe ="%s %s/%s %d" % (logger, logdir, logfile, LOGDURATION)
execve_path = PATH_TO_PYTHON_BINARY

# open the pipe to ROTATELOGS
so = se = os.popen(logpipe, 'w')

# re-open stdout without buffering
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

# redirect stdout and stderr to the log file opened above
os.dup2(so.fileno(), sys.stdout.fileno())
os.dup2(se.fileno(), sys.stderr.fileno()) 

# daemonize the calling process and replace it with the Tornado process
daemonize(no_close=True, pidfile=pidfile)
os.execv(execve_path, execve_args)
