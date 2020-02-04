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
""" Get experiments scenario tests """

import molotov
import aiohttp
from urllib.parse import urljoin
from iotlabcli.helpers import read_custom_api_url
from iotlabcli.auth import get_user_credentials

API_URL = 'https://www.iot-lab.info/api/'

@molotov.global_setup()
def init_test(args):
    url = read_custom_api_url() or API_URL
    molotov.set_var('url', url)
    username, passsword = get_user_credentials()
    molotov.set_var('auth', aiohttp.BasicAuth(username, passsword))


@molotov.events()
async def print_response(event, **info):
    if event == 'response_received':
        data = await info['response'].json()
        print(data)


@molotov.scenario(weight=50)
async def get_experiments_total(session):
    async with session.get(
            urljoin(molotov.get_var('url'), 'experiments/total'),
            auth=molotov.get_var('auth'),
    ) as resp:
        res = await resp.json()
        assert res['running'] is not None
        assert res['terminated'] is not None
        assert res['upcoming'] is not None
        assert resp.status == 200


@molotov.scenario(weight=50)
async def get_experiments_running(session):
    async with session.get(
            urljoin(molotov.get_var('url'), 'experiments/running'),
            auth=molotov.get_var('auth'),
    ) as resp:
        res = await resp.json()
        assert res['items'] is not None
        assert resp.status == 200
