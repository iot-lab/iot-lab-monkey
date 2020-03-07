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

from urllib.parse import urljoin
import molotov
import aiohttp
from aiohttp import FormData
from iotlabcli.experiment import _Experiment, AliasNodes
from iotlabcli.helpers import json_dumps
from .helpers import get_api_url, get_auth, generate_exp_name
from .helpers import get_test_site, get_test_users


@molotov.global_setup()
def init_test(args): #pylint: disable=W0613
    """ Adding test fixtures """
    molotov.set_var('url', get_api_url())
    molotov.set_var('auth', get_auth())
    molotov.set_var('site', get_test_site())
    molotov.set_var('users', get_test_users())


@molotov.events()
async def print_response(event, **info):
    """ Receive response event """
    if event == 'response_received':
        data = await info['response'].json()
        print(data)


@molotov.scenario(weight=100)
async def submit_experiment(session):
    """ Submit experiment scenario """
    users = molotov.get_var('users')
    if users.empty():
        print("No users ...")
        assert False
    user = users.get()
    # password = Monkey-<login>
    auth = aiohttp.BasicAuth(user, 'Monkey-{}'.format(user))
    exp = _Experiment(name=generate_exp_name(),
                      duration=20)
    alias = AliasNodes(1, molotov.get_var('site'), 'm3:at86rf231', False)
    exp.set_alias_nodes(alias)
    form = FormData()
    form.add_field("exp", json_dumps(exp),
                   content_type="multipart/form-data")
    async with session.post(
        urljoin(molotov.get_var('url'), 'experiments'),
        auth=auth,
        data=form,
    ) as resp:
        res = await resp.json()
        assert res['id'] is not None
        assert resp.status == 200
