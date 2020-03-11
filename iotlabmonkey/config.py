# -*- coding:utf-8 -*-

# This file is a part of IoT-LAB cli-tools
# Copyright (C) 2015 INRIA (Contact: admin@iot-lab.info)
# Contributor(s) : see AUTHORS file
#
# This software is governed by the CeCILL license under French law
# and abiding by the rules of distribution of free software.  You can  use,
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# http://www.cecill.info.
#
# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability.
#
# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.
""" Config file management """

import os
import json


def get_config():
    """ Get test config """
    try:
        # try override config file
        config = read_config_file('~/.iotlabmonkey/config.json')
    except IOError:
        config = read_config_file('iotlabmonkey/config.json')
    return config


def read_config_file(path):
    """ Open and read config file """
    with open(os.path.expanduser(path), 'r') as fconfig:  # expand '~'
        return json.load(fconfig)
