import pytest

from _pytest.logging import LogCaptureFixture

from pythclient.solana import SolanaClient, SolanaPublicKey
from pythclient.pythaccounts import PythAccount, PythAccountType, PythProductAccount


BCH_PRODUCT_ACCOUNT_KEY_DEVNET = '89GseEmvNkzAMMEXcW9oTYzqRPXTsJ3BmNerXmgA1osV'
BCH_PRICE_ACCOUNT_KEY_DEVNET = '4EQrNZYk5KR1RnjyzbaaRbHsv8VqZWzSUtvx58wLsZbj'

PRODUCT_ACCOUNT_B64_DATA = ('1MOyoQIAAAACAAAAlwAAADAClHlZh5cpDjY4oXEsKb3iNn0OynlPd4sltaRy8ZLeBnN5bWJvbAdCQ0gv'
                            'VVNECmFzc2V0X3R5cGUGQ3J5cHRvDnF1b3RlX2N1cnJlbmN5A1VTRAtkZXNjcmlwdGlvbgdCQ0gvVVNE'
                            'DmdlbmVyaWNfc3ltYm9sBkJDSFVTRARiYXNlA0JDSA==')


@pytest.fixture
def solana_pubkey():
    return SolanaPublicKey("AHtgzX45WTKfkPG53L6WYhGEXwQkN1BVknET3sVsLL8J")


@pytest.fixture
def pyth_account(solana_pubkey, solana_client):
    return PythAccount(
        key=solana_pubkey,
        solana=solana_client,
    )


@ pytest.fixture
def product_account(solana_client: SolanaClient) -> PythProductAccount:
    product_account = PythProductAccount(
        key=SolanaPublicKey(BCH_PRODUCT_ACCOUNT_KEY_DEVNET),
        solana=solana_client,
    )
    product_account.slot = 96866599
    product_account.attrs = {
        'asset_type': 'Crypto',
        'symbol': 'BCH/USD',
        'quote_currency': 'USD',
        'description': 'BCH/USD',
        'generic_symbol': 'BCHUSD',
        'base': 'BCH'
    }
    product_account.first_price_account_key = SolanaPublicKey(
        BCH_PRICE_ACCOUNT_KEY_DEVNET,
    )
    return product_account


def test_product_account_update_with_rpc_response_with_data(
    solana_client: SolanaClient,
    product_account: PythProductAccount
):
    actual = PythProductAccount(
        key=product_account.key,
        solana=solana_client,
    )
    assert actual.attrs == {}

    slot = 96866600
    value = {
        'lamports': 1000000000,
        'data': [
            PRODUCT_ACCOUNT_B64_DATA,
            'base64'
        ]
    }

    actual.update_with_rpc_response(slot=slot, value=value)
    assert actual.slot == slot
    assert actual.lamports == value['lamports']
    assert actual.attrs['symbol'] == product_account.attrs['symbol']
    assert actual.attrs['description'] == product_account.attrs['description']
    assert actual.attrs['generic_symbol'] == product_account.attrs['generic_symbol']
    assert actual.attrs['base'] == product_account.attrs['base']


def test_pyth_account_update_with_rpc_response_wrong_type(
    pyth_account: PythAccount,
    caplog: LogCaptureFixture
):
    slot = 96866600
    value = {
        'lamports': 1000000000,
        'data': [
            PRODUCT_ACCOUNT_B64_DATA,
            'base64'
        ]
    }

    exc_message = f"wrong Pyth account type {PythAccountType.PRODUCT} for {type(pyth_account)}"
    with pytest.raises(ValueError, match=exc_message):
        pyth_account.update_with_rpc_response(slot=slot, value=value)


def test_pyth_account_update_with_rpc_response_no_data(
    pyth_account: PythAccount,
    caplog: LogCaptureFixture
):
    slot = 106498726
    value = {
        "lamports": 1000000000
    }

    exc_message = f'invalid account data response from Solana for key {pyth_account.key}: {value}'
    with pytest.raises(ValueError, match=exc_message):
        pyth_account.update_with_rpc_response(slot=slot, value=value)
    assert exc_message in caplog.text
