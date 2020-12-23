import asyncio
import json
import platform
import sys
import time
import pytest
from traitlets.config import Config
from tornado.httpclient import HTTPClientError


@pytest.fixture(params=["MappingKernelManager", "AsyncMappingKernelManager"])
def jp_argv(request):
    return ["--ServerApp.kernel_manager_class=jupyter_server.services.kernels.kernelmanager." + request.param]


CULL_TIMEOUT = 10 if platform.python_implementation() == 'PyPy' else 2

@pytest.fixture
def jp_server_config():
    return Config({
        'ServerApp': {
            'MappingKernelManager': {
                'cull_idle_timeout': CULL_TIMEOUT,
                'cull_interval': 1,
                'cull_connected': False
            }
        }
    })


async def test_culling(jp_fetch, jp_ws_fetch):
    r = await jp_fetch(
        'api', 'kernels',
        method='POST',
        allow_nonstandard_methods=True
    )
    kernel = json.loads(r.body.decode())
    kid = kernel['id']

    # Open a websocket connection.
    ws = await jp_ws_fetch(
        'api', 'kernels', kid, 'channels'
    )

    r = await jp_fetch(
        'api', 'kernels', kid,
        method='GET'
    )
    model = json.loads(r.body.decode())
    assert model['connections'] == 1
    culled = await get_cull_status(kid, jp_fetch)  # connected, should not be culled
    assert not culled
    ws.close()
    culled = await get_cull_status(kid, jp_fetch)  # not connected, should be culled
    assert culled


async def get_cull_status(kid, jp_fetch):
    culled = False
    for i in range(20):  # Need max of 2x culling PERIOD ensure culling timeout exceeded
        try:
            r = await jp_fetch(
                'api', 'kernels', kid,
                method='GET'
            )
            kernel = json.loads(r.body.decode())
        except HTTPClientError as e:
            assert e.code == 404
            culled = True
            break
        else:
            await asyncio.sleep(CULL_TIMEOUT / 10.)
    return culled