import requests
import pexpect
import getpass
import argparse


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
    else:
        host = target_part
        port = 22

    if password:
        return user, password, host, port
    else:
        return user, host, port


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

    return host, port


def main():
    """
    Main application method.
    """
    args = parser.parse_args()

    connection_string_tuple = _get_target_connection_details(args.target_connection_string)
    if len(connection_string_tuple) == 4:
        user, password, host, port = connection_string_tuple
    else:
        user, host, port = connection_string_tuple
        password = getpass.getpass()

    metro_server_host, metro_server_port = _get_ssh_metro_server_connection_detail(args.ssh_metro_server_string)




if __name__ == '__main__':
    main()