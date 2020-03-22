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

import re
import asyncio
import molotov
from .config import get_config
from .helpers import get_test_ssh_key
from .helpers import get_test_experiments
from .helpers import get_api_url, get_auth, get_ipv6_prefix
from .scenario_test import get_experiment_nodes, flash_firmware
from .helpers import generate_riot_firmwares, get_test_firmwares
from .scenario_test import send_ssh_command


@molotov.global_setup()
def init_test(args): #pylint: disable=W0613
    """ Adding test fixtures """
    molotov.set_var('url', get_api_url())
    config = get_config()['riot_firmwares']
    generate_riot_firmwares(config['firmwares'],
                            config['nb_firmwares'])
    firmwares = get_test_firmwares(config['firmwares'])
    molotov.set_var('firmwares', firmwares)
    molotov.set_var('sshkey', get_test_ssh_key())
    molotov.set_var('exp', get_test_experiments())
    molotov.set_var('ipv6', get_ipv6_prefix())


# pylint: disable-msg=too-many-locals
@molotov.scenario(weight=100)
async def ipv6_border_router(session):
    """ IPv6 border router scenario """
    experiments = molotov.get_var('exp')
    if experiments.empty():
        print("No experiments ...")
        assert False
    # exp = (exp_id, login)
    exp = experiments.get()
    firmwares = molotov.get_var('firmwares')
    if firmwares.empty():
        print("No firmwares ...")
        assert False
    # firmware = {"firm1_name": "firm1_path",
    #             "firm2_name": "firm2_path"}
    firmware = firmwares.get()
    auth = get_auth(exp[1], 'Monkey-{}'.format(exp[1]))
    # Get nodes
    nodes = await asyncio.wait_for(
        get_experiment_nodes(session,
                             molotov.get_var('url'),
                             auth,
                             exp[0]),
        timeout=120)
    # Get BR node
    br_node = nodes.pop()
    # Flash other nodes
    firm = firmware['gnrc_networking']
    await asyncio.wait_for(
        flash_firmware(session,
                       molotov.get_var('url'),
                       auth,
                       exp[0],
                       firm,
                       nodes=[node['network_address'] for node in nodes]),
        timeout=120)
    # Flash BR node
    firm_br = firmware['gnrc_border_router']
    await asyncio.wait_for(
        flash_firmware(session,
                       molotov.get_var('url'),
                       auth,
                       exp[0],
                       firm_br,
                       nodes=[br_node['network_address']]),
        timeout=120)
    # Launch ethos_uhcpd
    # ipv6 = (tap_id, fdxx)
    ipv6 = molotov.get_var('ipv6').get()
    cmd = 'nohup sudo ethos_uhcpd.py {} tap{} {}::1/64 > /dev/null 2>&1 &'
    ethos_uhcpd_cmd = cmd.format(br_node['network_address'].split('.')[0],
                                 ipv6[0],
                                 ipv6[1])
    print(ethos_uhcpd_cmd)
    await asyncio.wait_for(
        send_ssh_command(br_node['network_address'],
                         exp[1],
                         molotov.get_var('sshkey'),
                         ethos_uhcpd_cmd),
        timeout=120)
    # wait DIO message BR -> node
    await asyncio.sleep(20)
    # Get one node
    node = nodes.pop()
    # Launch ifconfig command on the serial port
    ifconfig_cmd = '{} | nc -q 3 {} 20000'.format('echo ifconfig',
                                                  node['network_address'])
    output = await asyncio.wait_for(
        send_ssh_command(node['network_address'],
                         exp[1],
                         molotov.get_var('sshkey'),
                         ifconfig_cmd),
        timeout=120)
    if output:
        #inet6 addr: fe80::14b5:f765:106b:1115  scope: link  VAL
        #inet6 addr: fd00::14b5:f765:106b:1115  scope: global  VAL
        ipv6_addr = ipv6[1] + ':(:[0-9a-f]{0,4}){0,4}'
        ipv6_priv = ''
        for line in output.splitlines():
            if 'scope: global' in line:
                ipv6_priv = (re.search(re.compile(r'{}'.format(ipv6_addr)),
                                       line)).group()
        if ipv6_priv:
            # Launch ping6 command from the frontend SSH
            ping6_cmd = 'ping6 -c 1 {}'.format(ipv6_priv)
            output = await asyncio.wait_for(
                send_ssh_command(node['network_address'],
                                 exp[1],
                                 molotov.get_var('sshkey'),
                                 ping6_cmd),
                timeout=120)
            print(output)
        else:
            print('IPv6 global address not found')
