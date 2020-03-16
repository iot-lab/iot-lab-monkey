# -*- coding:utf-8 -*-

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
""" Access serial port scenario test """

import asyncio
import molotov
from .helpers import get_test_ssh_key
from .helpers import get_test_experiments
from .config import get_config
from .helpers import get_api_url, get_auth
from .scenario_test import get_experiment_nodes, send_ssh_command
from .scenario_test import flash_firmware


@molotov.global_setup()
def init_test(args): #pylint: disable=W0613
    """ Adding test fixtures """
    config = get_config()['serial_port']
    molotov.set_var('config', config)
    molotov.set_var('url', get_api_url())
    molotov.set_var('sshkey', get_test_ssh_key())
    molotov.set_var('exp', get_test_experiments())


@molotov.scenario(weight=100)
async def serial_port(session):
    """ Serial port scenario """
    experiments = molotov.get_var('exp')
    if experiments.empty():
        print("No experiments ...")
        assert False
    # exp = (exp_id, login)
    exp = experiments.get()
    auth = get_auth(exp[1], 'Monkey-{}'.format(exp[1]))
    nodes = await asyncio.wait_for(
        get_experiment_nodes(session,
                             molotov.get_var('url'),
                             auth,
                             exp[0]),
        timeout=120)
    # Get one node
    node = nodes.pop()
    config = molotov.get_var('config')
    firmware = 'iotlabmonkey/firmwares/{}'.format(config['firmware'])
    # Flash firmware
    await asyncio.wait_for(
        flash_firmware(session,
                       molotov.get_var('url'),
                       auth,
                       exp[0],
                       firmware,
                       [node['network_address']]),
        timeout=120)
    # Launch ifconfig command on the serial port
    #serial_cmd = '{} | socat - tcp:{}:20000'.format(config['cmd'],
    #                                                node['network_address'])
    serial_cmd = '{} | nc -q 1 {} 20000'.format(config['cmd'],
                                                node['network_address'])
    output = await asyncio.wait_for(
        send_ssh_command(node['network_address'],
                         exp[1],
                         molotov.get_var('sshkey'),
                         serial_cmd),
        timeout=120)
    print(output)
