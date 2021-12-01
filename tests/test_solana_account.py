from _pytest.logging import LogCaptureFixture
import pytest

from pytest_mock import MockerFixture

from mock import AsyncMock

from pythclient.solana import SolanaAccount, SolanaPublicKey, SolanaClient


@pytest.fixture
def solana_pubkey() -> SolanaPublicKey:
    return SolanaPublicKey("AHtgzX45WTKfkPG53L6WYhGEXwQkN1BVknET3sVsLL8J")


@pytest.fixture
def solana_account(solana_pubkey: SolanaPublicKey, solana_client: SolanaClient) -> SolanaAccount:
    return SolanaAccount(
        key=solana_pubkey,
        solana=solana_client,
    )


@pytest.fixture()
def mock_get_account_info(mocker: MockerFixture) -> AsyncMock:
    async_mock = AsyncMock()
    mocker.patch('pythclient.solana.SolanaClient.get_account_info', side_effect=async_mock)
    return async_mock


def test_solana_account_update_with_rpc_response(solana_account: SolanaAccount) -> None:
    assert solana_account.slot is None
    assert solana_account.lamports is None

    slot = 106498726
    value = {
        "lamports": 1000000000
    }

    solana_account.update_with_rpc_response(slot=slot, value=value)

    assert solana_account.slot == slot
    assert solana_account.lamports == value["lamports"]


@pytest.mark.asyncio
async def test_solana_account_update_success(solana_account: SolanaAccount,
                                             mock_get_account_info: AsyncMock) -> None:

    mock_get_account_info.return_value = {'context': {'slot': 93752509}, 'value': {'lamports': 1000000001}}

    await solana_account.update()
    assert solana_account.slot == mock_get_account_info.return_value['context']['slot']
    assert solana_account.lamports == mock_get_account_info.return_value['value']['lamports']


@pytest.mark.asyncio
async def test_solana_account_update_fail(solana_account: SolanaAccount,
                                          mock_get_account_info: AsyncMock,
                                          caplog: LogCaptureFixture,
                                          solana_pubkey: SolanaPublicKey) -> None:
    mock_get_account_info.return_value = {'value': {'lamports': 1000000001}}
    exc_message = f'error while updating account {solana_pubkey}'
    await solana_account.update()
    assert exc_message in caplog.text


@pytest.mark.asyncio
async def test_solana_account_update_null(solana_account: SolanaAccount,
                                          mock_get_account_info: AsyncMock,
                                          caplog: LogCaptureFixture,
                                          solana_pubkey: SolanaPublicKey,) -> None:
    mock_get_account_info.return_value = {'context': {'slot': 93752509}}
    exc_message = f'got null value from Solana getAccountInfo for {solana_pubkey}; ' \
        + f'non-existent account? {mock_get_account_info.return_value}'
    await solana_account.update()
    assert exc_message in caplog.text


def test_solana_account_str(solana_account: SolanaAccount) -> None:
    actual = str(solana_account)
    expected = f"SolanaAccount ({solana_account.key})"
    assert actual == expected
