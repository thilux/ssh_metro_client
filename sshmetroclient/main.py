import requests
import pexpect
import getpass
import argparse
import json
import time
import signal
import struct
import fcntl
import termios
import sys


parser = argparse.ArgumentParser()
parser.add_argument('target_connection_string', help='The connection string to the target machine. Can be provided in '
                                                     'the form of "user@machine_host:machine_port" or in the form '
                                                     '"user/password@machine_host:machine_port". In both cases, the '
                                                     'machine_port parameter can be omitted in which case the '
                                                     'application assumes port 22 by default')
parser.add_argument('ssh_metro_server_string', help='The specification of the SSH metro server to connect to. This '
                                                    'specification can be in the form of "server_host:server_port" or '
                                                    '"server_host". In the latter, the default SSH metro server 9871 is'
                                                    ' assumed.')

_METRO_API_PATH = 'api/v1/metro'
_INFO_API_PATH = 'api/v1/info'


def _get_target_connection_details(target_connection_string):
    """
    Returns a tuple with the raw connection details for the target machine extracted from the connection string provided
    in the application arguments. It is a specialized parser of that string.

    :param target_connection_string: the connection string provided in the arguments for the application.

    :return: A tuple in the form of (user, password, host, port) if a password is present in the connection string or
    (user, host, port) if a password is not present
    """

    password = None

    connection_string_format_error = 'Invalid connection string provided. Expected: user[/password]@host[:port]'

    if '@' not in target_connection_string:
        raise TypeError(connection_string_format_error)

    connection_string_parts = target_connection_string.split('@')

    if len(connection_string_parts) != 2:
        raise TypeError(connection_string_parts)

    authentication_part = connection_string_parts[0]
    target_part = connection_string_parts[1]

    if '/' in authentication_part:
        auth_parts = authentication_part.split('/')
        if len(auth_parts) != 2:
            raise TypeError(connection_string_format_error)

        user, password = auth_parts
    else:
        user = authentication_part

    if ':' in target_part:
        conn_parts = target_part.split(':')
        if len(conn_parts) != 2:
            raise TypeError(connection_string_format_error)
        host, port = conn_parts
        try:
            port = int(port)
        except ValueError:
            raise TypeError(connection_string_format_error)

    else:
        host = target_part
        port = 22

    if not len(user) or not len(host):
        raise TypeError(connection_string_format_error)

    if password:
        return user, password, host, int(port)
    else:
        return user, host, int(port)


def _get_ssh_metro_server_connection_detail(ssh_metro_server_conn_string):
    """
    Returns a tuple with the raw connection details for the SSH metro server provided in the application arguments. It
    is a specified parser for that string.

    :param ssh_metro_server_conn_string: the SSH metro server connection string.
    :return: A tuple in the form of (host, port)
    """

    connection_string_format_error = 'Invalid SSH metro connection string provided. Expected host[:port]'

    if ':' in ssh_metro_server_conn_string:
        conn_string_parts = ssh_metro_server_conn_string.split(':')
        if len(conn_string_parts) != 2:
            raise TypeError(connection_string_format_error)
        host, port = conn_string_parts
    else:
        host = ssh_metro_server_conn_string
        port = 9871

    return host, int(port)


def request_tunnel(username, password, host, port, metro_host, metro_port):
    """
    Issues a request to the metro server for a tunnel for an specified {host} and {port}, authenticated with a
    {username} and {password}.

    :param username: The username to connect to the indicated host.
    :param password: The password for the provided username
    :param host: The host to which a SSH tunnel is required
    :param port: The port on the host to which a SSH tunnel is required
    :param metro_host: The hostname where the SSH metro server is running
    :param metro_port: The port where the SSH metro server is listening to
    :return: a tuple in the form of (tunnel_host, tunnel_port)
    """
    headers = {'Content-Type': 'application/json'}
    data = dict()
    # data = {'username':'thilux', 'password':'P@uli2013', 'original_host':'192.168.0.211', 'original_port':22}
    data['username'] = username
    data['password'] = password
    data['original_host'] = host
    data['original_port'] = port

    api_url = 'http://%s:%d/%s' % (metro_host, metro_port, _METRO_API_PATH)

    response = requests.post(api_url, headers=headers, data=json.dumps(data))

    if response.status_code != 201:
        raise IOError('Error requesting tunnel to SSH metro server. Error from server: %s' %
                      response.json()['error'])

    response_dict = response.json()

    return response_dict['metro_host'], response_dict['metro_port']


def start_ssh_connection(username, password, host, port):
    """
    Starts the SSH connection to a host and port.

    :param username: The username to establish the SSH connection
    :param password: The password used for authentication
    :param host: The host of the SSH server
    :param port: The port of the SSH server
    """
    ssh_command = 'ssh %s@%s -p %d' % (username, host, port)
    child = pexpect.spawn(ssh_command)
    index = child.expect(['Are you sure you want to continue connecting', '[Pp]assword', 'refused', 'timed out',
                          'Could not resolve'])
    if index in (2, 3, 4):
        # Connection error
        raise IOError('Unable to connect to the specified SSH server!')
    if index == 0:
        child.sendline('yes')
        child.expect('[Pp]assword:')
    time.sleep(0.1)
    child.sendline(password)

    # Resizes the terminal based on the current window size of the terminal application being used.
    def resize_terminal():
        s = struct.pack('HHHH', 0, 0, 0, 0)
        try:
            # for testing no terminal is used so the below may fail with an IOerror and that is OK in this situation
            a = struct.unpack('hhhh', fcntl.ioctl(sys.stdout.fileno(), termios.TIOCGWINSZ, s))
            child.setwinsize(a[0], a[1])
        except IOError:
            pass

    # Handles the SIGWINCH signal and resizes the terminal accordingly
    def handle_sigwinch(signal, frames):
        resize_terminal()

    resize_terminal()

    signal.signal(signal.SIGWINCH, handle_sigwinch)
    child.interact()


def main(system_args):
    """
    Main application method.
    """
    args = parser.parse_args(system_args[1:])

    try:

        connection_string_tuple = _get_target_connection_details(args.target_connection_string)
        if len(connection_string_tuple) == 4:
            user, password, host, port = connection_string_tuple
        else:
            user, host, port = connection_string_tuple
            password = getpass.getpass()

        metro_server_host, metro_server_port = _get_ssh_metro_server_connection_detail(args.ssh_metro_server_string)

        tunnel_host, tunnel_port = request_tunnel(user, password, host, port, metro_server_host, metro_server_port)

        start_ssh_connection(user, password, tunnel_host, tunnel_port)
        # sys.exit(0)  # success
    except (IOError, TypeError) as err:
        print('ERROR: %s' % str(err))
        sys.exit(1)  # error


if __name__ == '__main__':
    main(sys.argv)
