import sshim
import re
import signal
import sys
import time

server = None


def shutdown(signal, frames):
    print('Fake SSH server received SIGTERM')
    if server is not None:
        server.stop()
        print('Server stopped!')

    sys.exit(0)


def ask_for_password(script):

    script.write('Password: ')
    groups = script.expect(re.compile('(?P<password>.*)')).groupdict()
    script.writeline('Logged in')
    server.stop()


signal.signal(signal.SIGTERM, shutdown)


def start_ssh_server(port):
    global server

    print('Starting fake SSH server on port %d' % port)

    server = sshim.Server(ask_for_password, port=port)
    try:

        server.run()
    except KeyboardInterrupt:
        server.stop()
