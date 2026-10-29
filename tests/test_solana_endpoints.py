"""Endpoint defaults are configured before importing the client modules."""

import json
import os
import subprocess
import sys

import pytest


ENDPOINTS = [
    ("DEVNET_ENDPOINT", "SOLANA_DEVNET_HTTP_ENDPOINT", "SOLANA_DEVNET_WS_ENDPOINT", "api.devnet.solana.com"),
    ("TESTNET_ENDPOINT", "SOLANA_TESTNET_HTTP_ENDPOINT", "SOLANA_TESTNET_WS_ENDPOINT", "api.testnet.solana.com"),
    ("MAINNET_ENDPOINT", "SOLANA_MAINNET_HTTP_ENDPOINT", "SOLANA_MAINNET_WS_ENDPOINT", "api.mainnet-beta.solana.com"),
    ("PYTHNET_ENDPOINT", "PYTHNET_HTTP_ENDPOINT", "PYTHNET_WS_ENDPOINT", "pythnet.rpcpool.com"),
    ("PYTHTEST_CROSSCHAIN_ENDPOINT", "PYTHTEST_CROSSCHAIN_HTTP_ENDPOINT", "PYTHTEST_CROSSCHAIN_WS_ENDPOINT",
     "api2.pythtest.pyth.network"),
    ("PYTHTEST_CONFORMANCE_ENDPOINT", "PYTHTEST_CONFORMANCE_HTTP_ENDPOINT", "PYTHTEST_CONFORMANCE_WS_ENDPOINT",
     "api2.pythtest.pyth.network"),
]


# A fresh interpreter also refreshes default arguments in PythClient without
# replacing classes that other tests have already imported. External connections
# are blocked; Python 3.9 may need a local socketpair when creating its event loop.
PROBE = """
import json
import os
import sys
from pytest_socket import disable_socket, socket_allow_hosts

if sys.platform == "win32":
    socket_allow_hosts(["127.0.0.1", "::1"], allow_unix_socket=True)
else:
    disable_socket(allow_unix_socket=True)
from pythclient import solana
from pythclient.pythclient import PythClient

options = json.loads(sys.argv[1])
arguments = options["arguments"]
def clients():
    direct = solana.SolanaClient(ratelimit=False, **arguments)
    wrapper = PythClient(
        first_mapping_account_key="11111111111111111111111111111111",
        **{"solana_" + key: value for key, value in arguments.items()},
    )
    return {
        "direct": [direct.endpoint, direct.ws_endpoint],
        "wrapper": [wrapper.solana.endpoint, wrapper.solana.ws_endpoint],
    }

result = clients()
result["constants"] = {
    name: getattr(solana, name) for name in options["constant_names"]
}
if options["later_host"] is not None:
    os.environ["DEVNET_ENDPOINT"] = options["later_host"]
    result["after_import"] = clients()
print(json.dumps(result))
"""


def probe(environment=None, arguments=None, later_host=None):
    environment = environment or {}
    process_env = os.environ.copy()
    for name, _, _, _ in ENDPOINTS:
        process_env.pop(name, None)
    process_env.update(environment)
    options = {
        "arguments": arguments or {},
        "later_host": later_host,
        "constant_names": [name for row in ENDPOINTS for name in row[:3]],
    }
    result = subprocess.run(
        [sys.executable, "-c", PROBE, json.dumps(options)],
        env=process_env,
        capture_output=True,
        text=True,
        check=True,
        timeout=20,
    )
    return json.loads(result.stdout)


def test_builtin_endpoint_defaults():
    result = probe()
    for name, http_name, ws_name, host in ENDPOINTS:
        assert result["constants"][name] == host
        assert result["constants"][http_name] == "https://" + host
        assert result["constants"][ws_name] == "wss://" + host
    assert result["direct"] == result["wrapper"] == [
        "https://api.devnet.solana.com", "wss://api.devnet.solana.com",
    ]


@pytest.mark.parametrize("name,http_name,ws_name,default_host", ENDPOINTS)
def test_environment_configures_each_network(name, http_name, ws_name, default_host):
    result = probe({name: "custom.example.invalid"})
    assert result["constants"][name] == "custom.example.invalid"
    assert result["constants"][http_name] == "https://custom.example.invalid"
    assert result["constants"][ws_name] == "wss://custom.example.invalid"


@pytest.mark.parametrize("host", ["localhost:8899", "[::1]:8899", "127.0.0.1:8899", "münich.example.invalid"])
def test_host_with_port(host):
    result = probe({"DEVNET_ENDPOINT": host})
    assert result["direct"] == result["wrapper"] == ["https://" + host, "wss://" + host]


@pytest.mark.parametrize("host", [
    "", " ", "\t\n", "https://rpc.example.invalid", "wss://rpc.example.invalid",
    "/rpc.example.invalid", "rpc.example.invalid/path", "rpc.example.invalid?key=value",
    "rpc.example.invalid#fragment", "user:password@rpc.example.invalid", "rpc example.invalid",
    "rpc.example.invalid\\path", "rpc.example.invalid:bad", ":8899",
    "rpc.example.invalid:65536", "rpc.example.invalid:0", "[invalid]", "[::1]suffix",
    "rpc.example.invalid:", "rpc..example.invalid", "-rpc.example.invalid", "rpc-.example.invalid",
    ".example.invalid", "999.999.999.999", "\x01rpc.example.invalid", "a" * 64 + ".example.invalid",
])
def test_empty_or_invalid_host_uses_builtin_default(host):
    result = probe({"DEVNET_ENDPOINT": host})
    assert result["constants"]["DEVNET_ENDPOINT"] == "api.devnet.solana.com"
    assert result["direct"] == result["wrapper"] == [
        "https://api.devnet.solana.com", "wss://api.devnet.solana.com",
    ]


def test_explicit_arguments_override_environment():
    result = probe(
        {"DEVNET_ENDPOINT": "environment.example.invalid"},
        {"endpoint": "http://explicit.example.invalid/rpc", "ws_endpoint": "ws://explicit.example.invalid/ws"},
    )
    assert result["direct"] == result["wrapper"] == [
        "http://explicit.example.invalid/rpc", "ws://explicit.example.invalid/ws",
    ]


@pytest.mark.parametrize("argument,index", [("endpoint", 0), ("ws_endpoint", 1)])
def test_one_explicit_argument_preserves_other_environment_default(argument, index):
    explicit = "https://explicit.example.invalid" if index == 0 else "wss://explicit.example.invalid"
    result = probe({"DEVNET_ENDPOINT": "environment.example.invalid"}, {argument: explicit})
    expected = ["https://environment.example.invalid", "wss://environment.example.invalid"]
    expected[index] = explicit
    assert result["direct"] == result["wrapper"] == expected


def test_invalid_environment_does_not_prevent_explicit_arguments():
    result = probe(
        {"DEVNET_ENDPOINT": "https://not-a-host.example.invalid/path"},
        {"endpoint": "https://explicit.example.invalid", "ws_endpoint": "wss://explicit.example.invalid"},
    )
    assert result["direct"] == result["wrapper"] == [
        "https://explicit.example.invalid", "wss://explicit.example.invalid",
    ]


def test_networks_are_configured_independently():
    result = probe({"DEVNET_ENDPOINT": "dev.example.invalid", "TESTNET_ENDPOINT": "test.example.invalid"})
    assert result["constants"]["SOLANA_DEVNET_HTTP_ENDPOINT"] == "https://dev.example.invalid"
    assert result["constants"]["SOLANA_TESTNET_WS_ENDPOINT"] == "wss://test.example.invalid"
    assert result["constants"]["MAINNET_ENDPOINT"] == "api.mainnet-beta.solana.com"


def test_environment_is_read_at_import_time():
    result = probe({"DEVNET_ENDPOINT": "initial.example.invalid"}, later_host="later.example.invalid")
    expected = ["https://initial.example.invalid", "wss://initial.example.invalid"]
    assert result["constants"]["DEVNET_ENDPOINT"] == "initial.example.invalid"
    assert result["direct"] == result["wrapper"] == expected
    assert result["after_import"]["direct"] == result["after_import"]["wrapper"] == expected
