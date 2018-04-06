"""
Unit tests for SSH metro client.

Run with:

$ python setup.py test
"""

import unittest
import socket
import time
from sshmetroclient import main as metroclient

from fake_ssh_server import start_ssh_server
from fake_metro_server import start_metro_server
from multiprocessing import Process

try:
    from unittest import mock
except ImportError:
    # for Python 2.7 unittest does not have mock, so a mock library is used instead.
    import mock


def get_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port


class CommandArgumentsTests(unittest.TestCase):

    def setUp(self):
        self.ssh_server_port = get_free_port()
        self.metro_server_port = get_free_port()
        self.ssh_server_thread = Process(target=start_ssh_server, args=(self.ssh_server_port,))
        self.ssh_server_thread.start()
        # start_ssh_server(self.ssh_server_port, {'test': 'abc123'})
        # start_metro_server(self.metro_server_port, 'localhost', self.ssh_server_port)
        self.metro_server_thread = Process(target=start_metro_server, args=(self.metro_server_port, 'localhost',
                                                                            self.ssh_server_port))
        self.metro_server_thread.start()

        # Metro server needs a little time to be fully started
        time.sleep(1)

    def tearDown(self):
        self.ssh_server_thread.terminate()
        self.metro_server_thread.terminate()

    @mock.patch('getpass.getpass')
    def test_no_arguments_passed(self, getpass):
        getpass.return_value = 'abc123'
        with self.assertRaises(SystemExit):
            metroclient.main(['main.py'])

    @mock.patch('getpass.getpass')
    def test_no_metro_server_argument(self, getpass):
        getpass.return_value = 'abc123'
        with self.assertRaises(SystemExit):
            metroclient.main(['main.py', 'testuser@localmachine'])

    @mock.patch('getpass.getpass')
    def test_no_target_machine_argument(self, getpass):
        getpass.return_value = 'abc123'
        with self.assertRaises(SystemExit):
            metroclient.main(['main.py', 'metroserver.com'])

    @mock.patch('getpass.getpass')
    def test_incorrect_format_target_machine_string_no_user(self, getpass):
        getpass.return_value = 'abc123'
        with self.assertRaises(SystemExit):
            metroclient.main(['main.py', '@localmachine', 'localhost:%d' % self.metro_server_port])

    @mock.patch('getpass.getpass')
    def test_incorrect_format_target_machine_string_missing_port(self, getpass):
        getpass.return_value = 'abc123'
        with self.assertRaises(SystemExit):
            metroclient.main(['main.py', 'user@localmachine:', 'localhost:%d' % self.metro_server_port])

    @mock.patch('getpass.getpass')
    def test_incorrect_format_target_machine_string_two_colons(self, getpass):
        getpass.return_value = 'abc123'
        with self.assertRaises(SystemExit):
            metroclient.main(['main.py', 'user@localmachine:55:33', 'localhost:%d' % self.metro_server_port])

    @mock.patch('getpass.getpass')
    def test_incorrect_format_target_machine_string_two_slashes(self, getpass):
        getpass.return_value = 'abc123'
        with self.assertRaises(SystemExit):
            metroclient.main(['main.py', 'user/password1/password2@localmachine', 'localhost:%d' %
                              self.metro_server_port])

    @mock.patch('getpass.getpass')
    def test_incorrect_format_target_machine_slash_misplaced(self, getpass):
        getpass.return_value = 'abc123'
        with self.assertRaises(SystemExit):
            metroclient.main(['main.py', 'username@localmachine/misplaced', 'localhost:%d' % self.metro_server_port])

    @mock.patch('getpass.getpass')
    def test_incorrect_format_target_machine_string_two_at(self, getpass):
        getpass.return_value = 'abc123'
        with self.assertRaises(SystemExit):
            metroclient.main(['main.py', 'user@machine1@machine2', 'localhost:%d' % self.metro_server_port])

    def test_password_included_in_target_machine_string(self):

        metroclient.main(['main.py', 'user/test123@localhost:2222', 'localhost:%d' % self.metro_server_port])


class ConnectingToMetroServer(unittest.TestCase):

    def setUp(self):
        self.ssh_server_port = get_free_port()
        self.metro_server_port = get_free_port()
        self.ssh_server_thread = Process(target=start_ssh_server, args=(self.ssh_server_port,))
        self.ssh_server_thread.start()
        # start_ssh_server(self.ssh_server_port, {'test': 'abc123'})
        # start_metro_server(self.metro_server_port, 'localhost', self.ssh_server_port)
        self.metro_server_thread = Process(target=start_metro_server, args=(self.metro_server_port, 'localhost',
                                                                                self.ssh_server_port))
        self.metro_server_thread.start()
        # Metro server needs a little time to be fully started
        time.sleep(1)

    def tearDown(self):
        self.ssh_server_thread.terminate()
        self.metro_server_thread.terminate()

    def test_successful_connection_password_included(self):

        metroclient.main(['main.py', 'user/test123@localhost:2222', 'localhost:%d' % self.metro_server_port])

    @mock.patch('getpass.getpass')
    def test_successfu_connection_password_given_later(self, getpass):
        getpass.return_value = 'abc123'

        metroclient.main(['main.py', 'user@localhost:2222', 'localhost:%d' % self.metro_server_port])

    def test_connection_failure_to_ssh_tunnel(self):
        with self.assertRaises(SystemExit):
            metroclient.main(['main.py', 'user/test123@ubxxyaojdoede.com:2222', 'localhost:%d' %
                              self.metro_server_port])

    def test_connection_to_not_refused_port(self):
        with self.assertRaises(SystemExit):
            metroclient.main(['main.py', 'user/test123@localhost:15', 'localhost:%d' % self.metro_server_port])