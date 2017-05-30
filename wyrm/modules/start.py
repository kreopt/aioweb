import sys
import os
from signal import SIGTERM

brief = "start the aioweb server"
aliases = ["s", "runserver"]

def usage(argv0):
    print("Usage: {} s [-d] [-p|--port N] [-h|--host HOST] [-c|--config YAML] [--pid PID] [-s|--socket SOCKET] [-S|--servers N]".format(argv0))
    sys.exit(1)

def execute(argv, argv0, engine):
    os.environ.setdefault("AIOWEB_SETTINGS_MODULE", "settings")
    sys.path.append(os.getcwd())

    import asyncio
    import logging
    import aioweb
    import getopt, yaml
    from daemonize import Daemonize
    from time import sleep
    from aioweb.conf import settings
    from aioweb.util.conf_reader import ConfigReader
    optlist, args = getopt.getopt(argv, "dhc:p:s:S:h:", ["help", "port=", "config=", "socket=", "servers=", "pid=", "host="])

    kwargs={}
    daemonize=False
    pid_file="aioweb.pid"
    if ('-h', '') in optlist or ('--help', '') in optlist:
        usage(argv0)

    config_file = "config/server.yml"
    for opt,val in optlist:
        if opt in ['--config', '-c']: config_file = val

    if os.path.exists(config_file):
        with open(config_file, "r") as f: conf = yaml.load(f.read())
        kwargs.update(conf.get("common", {}))
        env=os.environ.get('AIOWEB_ENV', 'development')
        kwargs.update(conf.get(env, {}))

    for opt,val in optlist:
        if opt in ['--port', '-p']:
            kwargs["port"] = int(val)
        elif opt in ['-d']:
            daemonize=True
        elif opt in ['-h', '--host']:
            kwargs["host"]=val
        elif opt in ['-s', '--socket']:
            kwargs["socket"]=val
        elif opt in ['-pid']:
            pid_file = val
        elif opt in ['-S', '--servers']:
            kwargs["servers"] = int(val)

    async def init(loop, argv):
        # setup application and extensions
        app = aioweb.Application(loop=loop)
        await app.setup()
        return app

    def runrunrun():
        # init logging
        logging.basicConfig(level=logging.DEBUG)

        loop = asyncio.get_event_loop()
        app = loop.run_until_complete(init(loop, argv))
        aioweb.start_app(app, **kwargs)

    if daemonize:
        if os.path.exists(pid_file):
            with open(pid_file, "r") as f: pid=int(f.read())
            print("killing process( PID: {} )".format(pid))
            try:
                os.kill(pid, SIGTERM)
                for i in range(0,10):
                    sleep(1)
                    if not os.path.exists(pid_file): break
            except ProcessLookupError:
                os.unlink(pid_file)

        Daemonize(app="aioweb", pid=pid_file, action=runrunrun, chdir=os.getcwd()).start()
    else:
        runrunrun()
