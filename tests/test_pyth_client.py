from typing import Any, Dict, Union, Sequence, List
import pytest
import base64
from pythclient.exceptions import NotLoadedException
from pythclient.pythaccounts import (
    _ACCOUNT_HEADER_BYTES, _VERSION_2, PythMappingAccount, PythPriceType, PythProductAccount, PythPriceAccount
)

from pythclient.pythclient import PythClient, WatchSession
from pythclient.solana import (
    SolanaClient,
    SolanaCommitment,
    SolanaPublicKey,
    SolanaPublicKeyOrStr
)

from pytest_mock import MockerFixture

from mock import AsyncMock


# Using constants instead of fixtures because:
# 1) these values are not expected to be mutated
# 2) these values are used in get_account_info_resp() and get_program_accounts_resp()
#    and so if they are passed in as fixtures, the functions will complain for the args
#    while mocking the respective functions
V2_FIRST_MAPPING_ACCOUNT_KEY = 'BmA9Z6FjioHJPpjT39QazZyhDRUdZy2ezwx4GiDdE2u2'
V2_PROGRAM_KEY = 'gSbePebfvPy7tRqimPoVecS2UsBvYv46ynrzWocc92s'

BCH_PRODUCT_ACCOUNT_KEY = '89GseEmvNkzAMMEXcW9oTYzqRPXTsJ3BmNerXmgA1osV'
BCH_PRICE_ACCOUNT_KEY = '4EQrNZYk5KR1RnjyzbaaRbHsv8VqZWzSUtvx58wLsZbj'

MAPPING_ACCOUNT_B64_DATA = ('1MOyoQIAAAABAAAAWAAAAAEAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAABqIGcc'
                            'Dj+MshnOP0blrglqTy/fk20r1NqJJfcAh9Ud2A==')
PRODUCT_ACCOUNT_B64_DATA = ('1MOyoQIAAAACAAAAlwAAADAClHlZh5cpDjY4oXEsKb3iNn0OynlPd4sltaRy8ZLeBnN5bWJvbAdCQ0gv'
                            'VVNECmFzc2V0X3R5cGUGQ3J5cHRvDnF1b3RlX2N1cnJlbmN5A1VTRAtkZXNjcmlwdGlvbgdCQ0gvVVNE'
                            'DmdlbmVyaWNfc3ltYm9sBkJDSFVTRARiYXNlA0JDSA==')
PRICE_ACCOUNT_B64_DATA = ('1MOyoQIAAAADAAAAEAsAAAEAAAD3////GwAAAAIAAAAfPsYFAAAAAB4+xgUAAAAA0B+GxYIAAAB/xYqq'
                          'AAAAADy4oy8BAAAAtPuFGgAAAAC8tR2HAAAAADy4oy8BAAAAAQAAAAAAAAAAAAAAAAAAAGogZxwOP4yy'
                          'Gc4/RuWuCWpPL9+TbSvU2okl9wCH1R3YAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAdPsYF'
                          'AAAAACB1G8yCAAAASJxHLgAAAAAvuzCkNjwQn8DZCsmCAAAASCynLwAAAAABAAAAAAAAAB8+xgUAAAAA'
                          'Qlxb88UapZ0T6mWzABhtX/lDiPrAaUMbsl4vmXpBgd4AI6GaggAAAICFtQ0AAAAAAQAAAAAAAAAdPsYF'
                          'AAAAAIATnJ2CAAAAAJW6CgAAAAABAAAAAAAAAB4+xgUAAAAAopQU2JDnE5ZYJwruatN5x2coYY19zVBC'
                          'tyZbiKhxYksAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
                          'AAAAAAAAAAAAAAAAkH6Erg47Ci94ZGUUYRxRICzgpNlfaIVeXC3eoge5K66z0OUXhQAAANMiBSEAAAAA'
                          'AQAAAAAAAABqYa8FAAAAALPQ5ReFAAAA0yIFIQAAAAABAAAAAAAAAGphrwUAAAAAJyCj9u7+AUmDcI1H'
                          'T9GvlDfStBYeQB5YYZZZsDQht+AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
                          'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAHkXfq/XM16tovM/VgEWSsYzNZhi/J9PvVgRbUtqgcg8dWmr8'
                          'ggAAADjoaxIAAAAAAQAAAAAAAAAcPsYFAAAAAIn1Af2CAAAAi/1rEgAAAAABAAAAAAAAAB0+xgUAAAAA'
                          'E3YWCAU39ntOTBHgm48UMpFVs7DvUTFB/bbaq/vZeC4AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
                          'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAXp50gnYmYi6R4+I+QnSWi4H88VJKoIye'
                          '5Uqoweh9l+UAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
                          'AAAAAAAAAAAAAAAAZk/hVoPBHzoEnahGCoRrjFSg5bWEvDQW7clr70r1C8UAAAAAAAAAAAAAAAAAAAAA'
                          'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAquLwEjnZE1h1qKp9'
                          'mpfiZ+fqJ1Rw3cLhX8nrx0VgKfEA599MkQAAAAB2sBAAAAAAAQAAAAAAAADCe1wFAAAAAADn30yRAAAA'
                          'AHawEAAAAAABAAAAAAAAAMJ7XAUAAAAANzRkq/Fg5DGQKTxjG3GJaaHanmhr9krIb1OThq282nAAAAAA'
                          'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
                          'dkkNS7shgAYOa/R2+DNwiO1TuFMlP/ht6SdRU3x62T0AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
                          'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAcTBWfR0upQv8cz+gPNHNt0GPnKBaObi9'
                          'LAKefxb5wtsAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
                          'AAAAAAAAAAAAAAAA1FflJlHKD2zpeTMZ6awJhRePbFADBPK0iyu32DjydxMAAAAAAAAAAAAAAAAAAAAA'
                          'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAQ4KPo2Gdpryu1okX'
                          '3h18zpIX3scrrhIwY/97590vlj7AoFlfkAAAAMDXGTAAAAAAAQAAAAAAAACokB0FAAAAAMCgWV+QAAAA'
                          'wNcZMAAAAAABAAAAAAAAAKiQHQUAAAAAf7Bx65O+Q/eDp7AcK8Lw03LmNh99Mpfu5nsydLpn2MUAAAAA'
                          'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
                          'GxE1Ex2rDAJyecg2P8ogqo9tPGKaDqZCf0+OHUfLz/EIHZd/hAAAALmp0SQAAAAAAQAAAAAAAADBxLcF'
                          'AAAAAAgdl3+EAAAAuanRJAAAAAABAAAAAAAAAMHEtwUAAAAAskWdp1YAT2k7uotwDoVkx9WSY7gay8uo'
                          'ykAsyQ6FrusAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
                          'AAAAAAAAAAAAAAAArq/eOgx1mU6Ixigj8cizk6fgfgXNTYnoHl9La1kz/CeAeCunjgAAAIDLeDEAAAAA'
                          'AQAAAAAAAABMtDcFAAAAAIB4K6eOAAAAgMt4MQAAAAABAAAAAAAAAEy0NwUAAAAA5v6vZs5/Kw4Sf3Gf'
                          'jLwRpg0NfHtESw5mRqECMnlwNLsAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
                          'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAZFIJBu0qw/EJSssd8apY//Qv+Wl5hRi697NmiqraVk0AAAAA'
                          'AAAAAAAAAAAAAAAAAAAAAAAAAADhxFoFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAOHEWgUAAAAA'
                          'jmNjneYqRRu77K9pGMTM31Dr7Hq6X3CAdoTOnMfxvKYAL4BmjwAAAIDR8AgAAAAAAQAAAAAAAAAch0YF'
                          'AAAAAAAvgGaPAAAAgNHwCAAAAAABAAAAAAAAAByHRgUAAAAAU8TtEyg6nKJ630rA85k7MfQylqJgcsND'
                          '5LnQsZ7hpLurmVVTjwAAAADC6wsAAAAAAQAAAAAAAADMjEYFAAAAAKuZVVOPAAAAAMLrCwAAAAABAAAA'
                          'AAAAAMyMRgUAAAAAmNhsxmReIdbBhxZ8WjXWTYNiwcVJPqEt0UqCDDpH5XYTB71SjwAAAAAcTg4AAAAA'
                          'AQAAAAAAAADcjEYFAAAAABMHvVKPAAAAABxODgAAAAABAAAAAAAAANyMRgUAAAAATvf0GXTayRqQxVor'
                          'MaSVHlP7Byc52vz8WQF/b2TeHGsvK9hRjwAAAIDfFxAAAAAAAQAAAAAAAADcjEYFAAAAAC8r2FGPAAAA'
                          'gN8XEAAAAAABAAAAAAAAANyMRgUAAAAADcMZLVXjwPNi+/UPw5fcAP5p0QpTeiI4ES5mWhy7pWQAAAAA'
                          'AAAAAAAAAAAAAAAAAAAAAAAAAADcjEYFAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAANyMRgUAAAAA'
                          'YW9iNZroU1iQRzOa1Eib/co4u8Na3Sv0XL7nFtovGb8AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
                          'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAASMRtW9UzBCNs7+OA+tYXWIAuPKUTI+uG'
                          '9WgYebtjLGYAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
                          'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
                          'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
                          'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
                          'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
                          'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
                          'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
                          'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
                          'AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA'
                          'AAAAAAAAAAAAAAAA')


def get_account_info_resp(key: Union[SolanaPublicKeyOrStr, Sequence[SolanaPublicKeyOrStr]]) -> Dict[str, Any]:
    b64_data = ''
    # mapping account
    if key == SolanaPublicKey(V2_FIRST_MAPPING_ACCOUNT_KEY):
        b64_data = MAPPING_ACCOUNT_B64_DATA
    # product account
    elif key == [SolanaPublicKey(BCH_PRODUCT_ACCOUNT_KEY)]:
        b64_data = PRODUCT_ACCOUNT_B64_DATA
    # price account
    elif key == SolanaPublicKey(BCH_PRICE_ACCOUNT_KEY):
        b64_data = PRICE_ACCOUNT_B64_DATA
    return {
        'context': {
            'slot': 96866599
        },
        'value': {
            'data': [
                b64_data,
                'base64'
            ]
        }
    }


def get_program_accounts_resp(key: SolanaPublicKeyOrStr,
                              commitment: str = SolanaCommitment.CONFIRMED,
                              encoding: str = "base64",
                              with_context: bool = True) -> Dict[str, Any]:
    return {
        'context': {
            'slot': 96866599
        },
        'value': [
            {
                'account': {
                    'data': [
                        MAPPING_ACCOUNT_B64_DATA,
                        'base64'
                    ],
                    'executable': False,
                    'lamports': 5143821440,
                    'owner': V2_PROGRAM_KEY,
                    'rentEpoch': 223
                },
                'pubkey': V2_FIRST_MAPPING_ACCOUNT_KEY
            },
            {
                'account': {
                    'data': [
                        PRODUCT_ACCOUNT_B64_DATA, 'base64'
                    ],
                    'executable': False,
                    'lamports': 4351231,
                    'owner': V2_PROGRAM_KEY,
                    'rentEpoch': 224
                },
                'pubkey': BCH_PRODUCT_ACCOUNT_KEY
            },
            {
                'account': {
                    'data': [
                        PRICE_ACCOUNT_B64_DATA,
                        'base64'
                    ],
                    'executable': False,
                    'lamports': 23942400,
                    'owner': V2_PROGRAM_KEY,
                    'rentEpoch': 224
                },
                'pubkey': BCH_PRICE_ACCOUNT_KEY
            }
        ]

    }


@ pytest.fixture
def pyth_client(solana_client: SolanaClient) -> PythClient:
    return PythClient(
        solana_client=solana_client,
        solana_endpoint="http://example.com",
        solana_ws_endpoint="ws://example.com",
        first_mapping_account_key=V2_FIRST_MAPPING_ACCOUNT_KEY,
        program_key=V2_PROGRAM_KEY
    )


@ pytest.fixture
def pyth_client_no_program_key(solana_client: SolanaClient) -> PythClient:
    return PythClient(
        solana_client=solana_client,
        solana_endpoint="http://example.com",
        solana_ws_endpoint="ws://example.com",
        first_mapping_account_key=V2_FIRST_MAPPING_ACCOUNT_KEY
    )


@ pytest.fixture
def watch_session(solana_client: SolanaClient) -> WatchSession:
    return WatchSession(solana_client)


@ pytest.fixture
def mapping_account(solana_client: SolanaClient) -> PythMappingAccount:
    mapping_account = PythMappingAccount(
        key=SolanaPublicKey(V2_FIRST_MAPPING_ACCOUNT_KEY),
        solana=solana_client
    )
    return mapping_account


@ pytest.fixture
def mapping_account_entries() -> List[SolanaPublicKey]:
    return [
        SolanaPublicKey(BCH_PRODUCT_ACCOUNT_KEY)
    ]


@ pytest.fixture
def product_account(solana_client: SolanaClient) -> PythProductAccount:
    product_account = PythProductAccount(
        key=SolanaPublicKey(BCH_PRODUCT_ACCOUNT_KEY),
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
        BCH_PRICE_ACCOUNT_KEY,
    )
    return product_account


@ pytest.fixture
def product_account_bytes() -> bytes:
    return base64.b64decode(PRODUCT_ACCOUNT_B64_DATA)[_ACCOUNT_HEADER_BYTES:]


@ pytest.fixture
def price_account(solana_client: SolanaClient) -> PythPriceAccount:
    return PythPriceAccount(
        key=SolanaPublicKey(BCH_PRICE_ACCOUNT_KEY),
        solana=solana_client,
    )


@ pytest.fixture
def price_account_bytes() -> bytes:
    return base64.b64decode(PRICE_ACCOUNT_B64_DATA)[_ACCOUNT_HEADER_BYTES:]


@pytest.fixture()
def mock_get_account_info(mocker: MockerFixture) -> AsyncMock:
    async_mock = AsyncMock(side_effect=get_account_info_resp)
    mocker.patch('pythclient.solana.SolanaClient.get_account_info', side_effect=async_mock)
    return async_mock


@ pytest.fixture()
def mock_get_program_accounts(mocker: MockerFixture) -> AsyncMock:
    async_mock = AsyncMock(side_effect=get_program_accounts_resp)
    mocker.patch('pythclient.solana.SolanaClient.get_program_accounts', side_effect=async_mock)
    return async_mock


def test_products_property_not_loaded(pyth_client: PythClient) -> None:
    with pytest.raises(NotLoadedException):
        pyth_client.products


@pytest.mark.asyncio
async def test_get_products(
    pyth_client: PythClient,
    mock_get_account_info: AsyncMock,
    product_account: PythProductAccount
) -> None:
    products = await pyth_client.get_products()
    for i, _ in enumerate(products):
        assert products[i].key == product_account.key


def test_get_ratelimit(
    pyth_client: PythClient,
) -> None:
    ratelimit = pyth_client.solana_ratelimit
    assert ratelimit._get_overall_interval() == 0
    assert ratelimit._get_method_interval() == 0
    assert ratelimit._get_connection_interval() == 0

    ratelimit.configure(overall_cps=1, method_cps=1, connection_cps=1)
    assert ratelimit._get_overall_interval() == 1.0
    assert ratelimit._get_method_interval() == 1.0
    assert ratelimit._get_connection_interval() == 1.0


@pytest.mark.asyncio
async def test_get_mapping_accounts(
    pyth_client: PythClient,
    mock_get_account_info: AsyncMock,
    mapping_account: PythMappingAccount
) -> None:
    mapping_accounts = await pyth_client.get_mapping_accounts()
    assert len(mapping_accounts) == 1
    assert mapping_accounts[0].key == mapping_account.key

    # call get_mapping_accounts again to test pyth_client returns self._mapping_accounts since
    # it has been populated due to previous call
    mapping_accounts = await pyth_client.get_mapping_accounts()
    assert len(mapping_accounts) == 1
    assert mapping_accounts[0].key == mapping_account.key


@pytest.mark.asyncio
async def test_get_all_accounts(
    pyth_client: PythClient,
    mock_get_account_info: AsyncMock,
    mapping_account: PythMappingAccount,
    mapping_account_entries: List[SolanaPublicKey],
    product_account: PythProductAccount,
    price_account: PythPriceAccount,
    product_account_bytes: bytes,
    price_account_bytes: bytes
) -> None:
    products = await pyth_client.get_products()
    for product in products:
        product.update_from(buffer=product_account_bytes, version=_VERSION_2)
        prices = await product.get_prices()
        for price in prices.values():
            price.update_from(buffer=price_account_bytes, version=_VERSION_2)

    accounts = await pyth_client.get_all_accounts()
    assert accounts[0].key == mapping_account.key
    assert accounts[0].entries == mapping_account_entries
    assert dict(accounts[1]) == dict(product_account)
    assert accounts[2].key == price_account.key
    assert accounts[2].price_type == PythPriceType.PRICE
    assert accounts[2].exponent == -9
    assert accounts[2].num_components == 27
    assert len(accounts[2].price_components) == accounts[2].num_components
    assert accounts[2].last_slot == 96878111
    assert accounts[2].valid_slot == 96878110
    assert accounts[2].product_account_key == product_account.key
    assert accounts[2].next_price_account_key is None


@ pytest.mark.asyncio
async def test_refresh_all_prices(
    pyth_client: PythClient,
    mock_get_account_info: AsyncMock,
    mock_get_program_accounts: AsyncMock,
    product_account: PythProductAccount,
    price_account: PythPriceAccount
) -> None:
    await pyth_client.refresh_all_prices()
    for product in pyth_client.products:
        account = product.prices[PythPriceType.PRICE]
        assert account.key == price_account.key
        assert account.price_type == PythPriceType.PRICE
        assert account.exponent == -9
        assert account.num_components == 27
        assert len(account.price_components) == account.num_components
        assert account.last_slot == 96878111
        assert account.valid_slot == 96878110
        assert account.product_account_key == product_account.key
        assert account.next_price_account_key is None


@ pytest.mark.asyncio
async def test_refresh_all_prices_no_program_key(
    pyth_client_no_program_key: PythClient,
    mock_get_account_info: AsyncMock,
) -> None:
    await pyth_client_no_program_key.refresh_all_prices()
    for product in pyth_client_no_program_key.products:
        with pytest.raises(NotLoadedException):
            product.prices


def test_create_watch_session(
    pyth_client: PythClient,
    watch_session: WatchSession
) -> None:
    ws = pyth_client.create_watch_session()
    assert isinstance(ws, WatchSession)
