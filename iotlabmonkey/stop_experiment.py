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
""" Stop experiment scenario test """

from urllib.parse import urljoin
import molotov
import aiohttp
from .helpers import get_api_url
from .helpers import get_test_experiments


@molotov.global_setup()
def init_test(args): #pylint: disable=W0613
    """ Adding test fixtures """
    molotov.set_var('url', get_api_url())
    molotov.set_var('exp', get_test_experiments())


@molotov.events()
async def print_response(event, **info):
    """ Receive response event """
    if event == 'response_received':
        data = await info['response'].json()
        print(data)


@molotov.scenario(weight=100)
async def stop_experiment(session):
    """ Stop experiment scenario """
    experiments = molotov.get_var('exp')
    if experiments.empty():
        print("No experiments ...")
        assert False
     # exp = (exp_id, login)
    exp = experiments.get()
    # password = Monkey-<login>
    auth = aiohttp.BasicAuth(exp[1], 'Monkey-{}'.format(exp[1]))
    async with session.delete(
        urljoin(molotov.get_var('url'), 'experiments/{}'.format(exp[0])),
        auth=auth,
    ) as resp:
        res = await resp.json()
        assert res['id'] is not None
        assert resp.status == 200
