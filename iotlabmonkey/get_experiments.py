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
""" Get experiments scenario test """

from urllib.parse import urljoin
import molotov
from .helpers import get_api_url, get_auth


@molotov.global_setup()
def init_test(args): #pylint: disable=W0613
    """ Adding test fixtures """
    molotov.set_var('url', get_api_url())
    molotov.set_var('auth', get_auth())


@molotov.events()
async def print_response(event, **info):
    """ Receive response event """
    if event == 'response_received':
        data = await info['response'].json()
        print(data)


@molotov.scenario(weight=50)
async def get_experiments_total(session):
    """ Scenario get total experiments """
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
    """ Get experiments scenario """
    async with session.get(
        urljoin(molotov.get_var('url'), 'experiments/running'),
        auth=molotov.get_var('auth'),
    ) as resp:
        res = await resp.json()
        assert res['items'] is not None
        assert resp.status == 200
