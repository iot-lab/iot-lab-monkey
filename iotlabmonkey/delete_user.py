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
""" Delete user scenario test """

from urllib.parse import urljoin
import molotov
from .helpers import get_api_url, get_auth
from .helpers import get_test_users


@molotov.global_setup()
def init_test(args): #pylint: disable=W0613
    """ Adding test fixtures """
    molotov.set_var('url', get_api_url())
    molotov.set_var('auth', get_auth())
    molotov.set_var('users', get_test_users())


@molotov.scenario(weight=100)
async def delete_user(session):
    """ Delete user scenario """
    users = molotov.get_var('users')
    if users.empty():
        print("No users ...")
        assert False
    user = users.get()
    async with session.delete(
        urljoin(molotov.get_var('url'), 'users/{}'.format(user)),
        auth=molotov.get_var('auth'),
        params={'mailing-list': 'off'}
    ) as resp:
        assert resp.status == 204
