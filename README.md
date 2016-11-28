xivo-amid
=========
[![Build Status](https://travis-ci.org/xivo-pbx/xivo-amid.png?branch=master)](https://travis-ci.org/xivo-pbx/xivo-amid)

xivo-amid is a daemon for interacting Asterisk's AMI:

* forward AMI events to RabbitMQ
* expose HTTP JSON interface for AMI actions


Docker
------

The xivo/amid image can be built using the following command:

   % docker build -t wazopbx/xivo-amid .


Testing
-------

xivo-amid contains unittests and integration tests


Running unit tests
------------------

```
apt-get install libpq-dev python-dev libffi-dev libyaml-dev
pip install tox
tox --recreate -e py27
```


Running integration tests
-------------------------

You need Docker installed.

```
cd integration_tests
pip install -U -r test-requirements.txt
make test-setup
make test
```
