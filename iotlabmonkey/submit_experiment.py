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
""" Submit experiment scenario test """

import molotov
import aiohttp
import random
import string
from aiohttp import FormData
from urllib.parse import urljoin
from iotlabcli.experiment import _Experiment, AliasNodes
from iotlabcli.helpers import json_dumps, read_custom_api_url
from iotlabcli.auth import get_user_credentials


API_URL = 'https://www.iot-lab.info/api/'


@molotov.global_setup()
def init_test(args):
    url = read_custom_api_url() or API_URL
    molotov.set_var('url', url)
    username, passsword = get_user_credentials()
    molotov.set_var('auth', aiohttp.BasicAuth(username, passsword))
    sites_dict = molotov.json_request(urljoin(url, 'sites'))['content']
    sites = [site["site"] for site in sites_dict["items"]]
    molotov.set_var('site', [site for site in sites if 'grenoble' in site][0])


@molotov.events()
async def print_response(event, **info):
    if event == 'response_received':
        data = await info['response'].json()
        print(data)


def random_name(stringLength=10):
    letters = string.ascii_lowercase
    return 'monkey'.join(random.choice(letters) for i in range(6))


@molotov.scenario(weight=100)
async def submit_experiment(session):
    rand_char = ''.join(random.choice(string.ascii_lowercase) for x in range(6))
    exp = _Experiment(name= '{}{}'.format('monkey', rand_char),
                      duration=20)
    alias = AliasNodes(1, molotov.get_var('site'), 'm3:at86rf231', False)
    exp.set_alias_nodes(alias)
    form = FormData()
    form.add_field("exp", json_dumps(exp),
                   content_type="multipart/form-data")
    async with session.post(
            urljoin(molotov.get_var('url'), 'experiments'),
            auth=molotov.get_var('auth'),
            data=form,
    ) as resp:
        res = await resp.json()
        assert res['id'] is not None
        assert resp.status == 200
