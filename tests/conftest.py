import logging
import pytest
from _pytest.logging import caplog as _caplog
from pythclient.solana import SolanaClient
from loguru import logger


@pytest.fixture
def solana_client():
    return SolanaClient(
        endpoint="https://example.com",
        ws_endpoint="wss://example.com",
    )


@pytest.fixture
def caplog(_caplog):
    logger.enable("pythclient")

    class PropogateHandler(logging.Handler):
        def emit(self, record):
            logging.getLogger(record.name).handle(record)

    handler_id = logger.add(PropogateHandler(), format="{message}")
    yield _caplog
    logger.remove(handler_id)
