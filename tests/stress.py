""" stress tests """
import aiohttp
import molotov
from iotlabclient.auth import get_user_credentials

API = 'https://devwww.iot-lab.info/api/'
username, passsword = get_user_credentials()
auth = aiohttp.BasicAuth(username, passsword)
states = 'Terminated,Stopped,Error,Running,Finishing,Resuming,toError,Waiting,Launching,Hold,toLaunch,toAckReservation,Suspended'


@molotov.events()
async def print_response(event, **info):
    if event == 'response_received':
        data = await info['response'].json()
        print(data)


@molotov.scenario(weight=1)
async def dashboard(session):
    async with session.get(
            API + 'experiments/total/all',
            auth=auth,
            params=dict(
                state=states,
            )
    ) as resp:
        res = await resp.json()
        assert res['running'] is not None
        assert res['terminated'] is not None
        assert res['upcoming'] is not None
        assert resp.status == 200
