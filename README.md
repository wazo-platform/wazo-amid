# wazo-amid
[![Build Status](https://jenkins.wazo.community/buildStatus/icon?job=wazo-amid)](https://jenkins.wazo.community/job/wazo-amid)

wazo-amid is a daemon for interacting with Asterisk's AMI:

* forward AMI events to RabbitMQ
* expose HTTP JSON interface for AMI actions


## Docker

The wazoplatform/wazo-ami image can be built using the following command:

    docker build -t wazoplatform/wazo-amid .


## Testing

wazo-amid contains unittests and integration tests


### Running unit tests

You need the following installed:
    - python3.9
    - python3.9-distutils

```
apt-get install libpq-dev python3-dev libffi-dev libyaml-dev
pip install tox
tox --recreate -e py39
```


### Running integration tests

You need the following installed:
    - Docker
    - python3.9
    - python3.9-distutils

```
cd integration_tests
pip install -U -r test-requirements.txt
make test-setup
make test
```
