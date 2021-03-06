# Copyright 2017-2020 The Wazo Authors  (see the AUTHORS file)
# SPDX-License-Identifier: GPL-3.0-or-later

import os

from wazo_amid.ami.parser import parse_buffer

__location__ = os.path.realpath(os.path.join(os.getcwd(), os.path.dirname(__file__)))


def pass_(*args, **kwargs):
    pass


with open(os.path.join(__location__, 'ami-messages.txt'), 'rb') as f:
    sample = f.read().replace('\n', '\r\n')

ami_stream = sample * 50

parse_buffer(ami_stream, pass_, pass_)
