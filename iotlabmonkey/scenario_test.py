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
""" Scenario test """

from urllib.parse import urljoin
import json
import asyncssh
from aiohttp import FormData


async def get_experiment_nodes(session, url, auth, exp_id):
    """ Get experiment nodes"""
    async with session.get(
        urljoin(url,
                'experiments/{}/nodes'.format(exp_id)),
        auth=auth,
    ) as resp:
        res = await resp.json()
        assert res['items'] is not None
        assert resp.status == 200
    return [node for node in res["items"]]


# pylint: disable=too-many-arguments
async def flash_firmware(session, url, auth, exp_id, firm_path, nodes=None):
    """ Flash firmware """
    form = FormData()
    form.add_field('file',
                   open(firm_path, 'rb'),
                   filename="firmware",
                   content_type="application/octet-stream")
    if nodes:
        form.add_field("nodes", json.dumps(nodes),
                       content_type="application/json")
    url_flash = 'experiments/{}/nodes/flash'.format(exp_id)
    async with session.post(
        urljoin(url, url_flash),
        auth=auth,
        data=form,
    ) as resp:
        res = await resp.json()
        if not "0" in res and not "1" in res:
            assert False
        assert resp.status == 200


async def send_ssh_command(node, login, keys, cmd):
    """ Send SSH command """
    frontend_fqdn = '{}.iot-lab.info'.format(node.split('.')[1])
    try:
        async with asyncssh.connect(frontend_fqdn,
                                    username=login,
                                    client_keys=[keys]) as conn:
            result = await conn.run(cmd)
            if result.exit_status == 0:
                return result.stdout
            return result.stderr
    except (OSError, asyncssh.Error) as exc:
        print('SSH connection failed: ' + str(exc))
        assert False
