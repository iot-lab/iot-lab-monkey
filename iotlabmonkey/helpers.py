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
""" Helpers test functions """

import random
import string
from queue import Queue
from urllib.parse import urljoin
import molotov
import aiohttp
from iotlabcli.helpers import read_custom_api_url
from iotlabcli.auth import get_user_credentials


API_URL = 'https://www.iot-lab.info/api/'
TEST_SITE = 'grenoble'
TEST_GROUP = 'monkey-test'
MAX_TEST_USERS = 3000


def get_api_url():
    """ Return API url """
    return read_custom_api_url() or API_URL


def get_auth():
    """ Return Basic Auth credentials """
    username, passsword = get_user_credentials()
    return aiohttp.BasicAuth(username, passsword)


def get_test_users():
    """ Return test users """
    # thread-safe structure for molotov workers/processes
    users = Queue()
    groups = molotov.json_request(urljoin(get_api_url(), 'groups'),
                                  auth=get_auth())['content']
    group = [group for group in groups if group['name'] == TEST_GROUP]
    # check if group exists
    if group:
        for user in group[0]['users']:
            users.put(user)
    return users


def get_test_experiments():
    """ Return test experiments """
    url = urljoin(get_api_url(), 'experiments/running')
    exp_running = molotov.json_request(url)['content']
    exp_test = [(exp["id"], exp["user"]) for exp
                in exp_running["items"]
                if 'monkey' in exp['name']]
    # thread-safe structure for molotov workers/processes
    experiments = Queue()
    if exp_test:
        for exp in exp_test:
            experiments.put(exp)
    return experiments


def get_test_site():
    """ Return test site """
    url = urljoin(get_api_url(), 'sites')
    sites_dict = molotov.json_request(url)['content']
    sites = [site["site"] for site in sites_dict["items"]]
    return [site for site in sites if TEST_SITE in site][0]


def generate_test_users():
    """ Generate test users """
    # thread-safe structure for molotov workers/processes
    users = Queue(maxsize=MAX_TEST_USERS)
    for user in generate_login(MAX_TEST_USERS):
        users.put(create_test_user(user))
    return users


def rand_lower(num):
    """ Return random lowercase string characters """
    return  ''.join(random.choice(string.ascii_lowercase) for x in range(num))


def generate_exp_name():
    """ Generate experiment name """
    return '{}{}'.format('monkey', rand_lower(6))


def generate_login(num):
    """ Generate random username """
    for index in range(num):
        yield '{}{}'.format(rand_lower(7), index+1)


def create_test_user(username):
    """ Create user """
    return {'motivations': 'Monkey stress test',
            'category': 'Academic',
            'city': TEST_SITE,
            'organization': 'INRIA',
            'country': 'France',
            'firstName': username,
            'lastName': username,
            'login': username,
            # add one special and uppercase character
            'password': 'Monkey-{}'.format(username),
            'groups': [TEST_GROUP],
            'email': '{}@monkey.fr'. format(username)}
