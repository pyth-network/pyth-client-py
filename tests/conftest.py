import pytest
from pythclient.solana import SolanaClient


@pytest.fixture
def solana_client():
    return SolanaClient(
        endpoint="https://example.com",
        ws_endpoint="wss://example.com",
    )
