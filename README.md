## SSH metro client

[![Build Status](https://travis-ci.org/thilux/ssh_metro_client.svg?branch=master)](https://travis-ci.org/thilux/ssh_metro_client) [![codecov](https://codecov.io/gh/thilux/ssh_metro_client/branch/master/graph/badge.svg)](https://codecov.io/gh/thilux/ssh_metro_client)

Client application to communicate and connect to SSH tunnels started by an [SSH metro server]().

The functionalities of this application is limited to request for SSH tunnels creation in an SSH metro server and connect to it via SSH.

### Technology

SSH metro client uses the following libraries for the specified purpose:

* Requests: The famous and incredible HTTP Requests library to communicate to the SSH metro server.
* Pexpect: To handled operating system level commands to start an SSH connection to the SSH tunnel.

### Installation

To install SSH metro client, just run the following command on your machine:

```
$> pip install ssh-metro-client
```

or

```
$> pipenv install ssh-metro-client
```

### Running

To start SSH metro client, you need to specify the details of the target host you want to connect through SSH and the details of the SSH metro server. As an example, you can run a command like the below on your terminal:

```
$> ssh_metro_client user@targetmachine_host:targetmachine_port sshmetroserver_host:sshmetroserver_port
```

The above command prompts for a password to be provided for the `user` on the target machine `targetmachine_host`. The command below, however, specifies the password for the user as part of the command:

```
$> ssh_metro_client user/password@targetmachine_host:targetmachine_port sshmetroserver_host:sshmetroserver_port
```

For security reasons, the former is recommended.

### Developers

Currently, this project is maintained and developed by:

* thilux (Thiago Santana)

Contributions are expected and more than welcome. If you have ideas to enhance the solution, please raise and issue and specify your request. The same is required if you simply want to report bugs. If you want to contribute with code, fork the project and submit a pull request and it will be surely reviewed and happily accepted.

### License

Copyright 2018 Thiago Santana (thilux).

Licensed to the Apache Software Foundation (ASF) under one or more contributor license agreements. See the NOTICE file distributed with this work for additional information regarding copyright ownership. The ASF licenses this file to you under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at

http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.