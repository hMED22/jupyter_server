import pytest


@pytest.fixture
def server_config(template_dir):
    return {
            "ServerApp": {
                "jpserver_extensions": {
                    "tests.extension.mockextensions": True
                }
            },
            "MockExtensionApp": {
                "template_paths": [
                    str(template_dir)
                ]
            }
        }


async def test_handler(fetch):
    r = await fetch(
        'mock',
        method='GET'
    )
    assert r.code == 200
    assert r.body.decode() == 'mock trait'


async def test_handler_template(fetch, mock_template):
    r = await fetch(
        'mock_template',
        method='GET'
    )
    assert r.code == 200


@pytest.mark.parametrize(
    'server_config',
    [
        {
            "ServerApp": {
                "jpserver_extensions": {
                    "tests.extension.mockextensions": True
                }
            },
            "MockExtensionApp": {
                # Change a trait in the MockExtensionApp using
                # the following config value.
                "mock_trait": "test mock trait"
            }
        }
    ]
)
async def test_handler_setting(fetch):
    # Test that the extension trait was picked up by the webapp.
    r = await fetch(
        'mock',
        method='GET'
    )
    assert r.code == 200
    assert r.body.decode() == 'test mock trait'


@pytest.mark.parametrize(
    'argv', (['--MockExtensionApp.mock_trait="test mock trait"'],)
)
async def test_handler_argv(fetch):
    # Test that the extension trait was picked up by the webapp.
    r = await fetch(
        'mock',
        method='GET'
    )
    assert r.code == 200
    assert r.body.decode() == 'test mock trait'


@pytest.mark.parametrize(
    'server_config',
    [
        {
            "ServerApp": {
                "jpserver_extensions": {
                    "tests.extension.mockextensions": True
                },
                # Move extension handlers behind a url prefix
                "base_url": "test_prefix"
            },
            "MockExtensionApp": {
                # Change a trait in the MockExtensionApp using
                # the following config value.
                "mock_trait": "test mock trait"
            }
        }
    ]
)
async def test_base_url(fetch):
    # Test that the extension's handlers were properly prefixed
    r = await fetch(
        'test_prefix', 'mock',
        method='GET'
    )
    assert r.code == 200
    assert r.body.decode() == 'test mock trait'

    # Test that the static namespace was prefixed by base_url
    r = await fetch(
        'test_prefix',
        'static', 'mockextension', 'mock.txt',
        method='GET'
    )
    assert r.code == 200
    body = r.body.decode()
    assert "mock static content" in body
