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
""" IPv6 border router scenario test """

import asyncio
import molotov
from .helpers import get_test_ssh_key
from .helpers import get_test_experiments
from .helpers import get_api_url, get_auth, get_ipv6_prefix
from .scenario_test import get_experiment_nodes, flash_firmware
from .scenario_test import send_ssh_command

@molotov.global_setup()
def init_test(args): #pylint: disable=W0613
    """ Adding test fixtures """
    molotov.set_var('url', get_api_url())
    molotov.set_var('sshkey', get_test_ssh_key())
    molotov.set_var('exp', get_test_experiments())
    molotov.set_var('ipv6', get_ipv6_prefix())


@molotov.events()
async def print_response(event, **info):
    """ Receive response event """
    if event == 'response_received':
        data = await info['response'].json()
        print(data)


@molotov.scenario(weight=100)
async def ipv6_border_router(session):
    """ IPv6 border router scenario """
    experiments = molotov.get_var('exp')
    if experiments.empty():
        print("No experiments ...")
        assert False
    # exp = (exp_id, login)
    exp = experiments.get()
    auth = get_auth(exp[1], 'Monkey-{}'.format(exp[1]))
    # Get nodes
    nodes = await asyncio.wait_for(
        get_experiment_nodes(session,
                             molotov.get_var('url'),
                             auth,
                             exp[0]),
        timeout=120)
    # Get BR node
    node = nodes.pop()
    print('BR node: {}'.format(node['network_address']))
    firm_path = 'iotlabmonkey/firmwares/{}'
    # Flash BR node
    await asyncio.wait_for(
        flash_firmware(session,
                       molotov.get_var('url'),
                       auth,
                       exp[0],
                       firm_path.format('gnrc_border_router.elf'),
                       nodes=[node['network_address']]),
        timeout=120)
    # Flash other nodes
    await asyncio.wait_for(
        flash_firmware(session,
                       molotov.get_var('url'),
                       auth,
                       exp[0],
                       firm_path.format('gnrc_networking.elf'),
                       nodes=[node['network_address'] for node in nodes]),
        timeout=120)
    # Launch ethos_uhcpd
    # ipv6 = (tap_id, fdxx)
    ipv6 = molotov.get_var('ipv6').get()
    cmd = 'nohup sudo ethos_uhcpd.py {} tap{} {}::1/64 > /dev/null 2>&1 &'
    ethos_uhcpd_cmd = cmd.format(node['network_address'].split('.')[0],
                                 ipv6[0],
                                 ipv6[1])
    print(ethos_uhcpd_cmd)
    #ipv6_addr = fd02::245f:f965:106b:1114
    await asyncio.wait_for(
        send_ssh_command(node['network_address'],
                         exp[1],
                         molotov.get_var('sshkey'),
                         ethos_uhcpd_cmd),
        timeout=120)
