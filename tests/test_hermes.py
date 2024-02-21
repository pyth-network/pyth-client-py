import pytest

from pytest_mock import MockerFixture

from mock import AsyncMock

from pythclient.hermes import HermesClient, PriceFeed, parse_unsupported_version

@pytest.fixture
def feed_ids():
    return ["e62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43"]

@pytest.fixture
def hermes_client(feed_ids):
    return HermesClient(feed_ids)

@pytest.fixture
def data_v1():
    return {
        "ema_price": {
            "conf": "509500001",
            "expo": -8,
            "price": "2920679499999",
            "publish_time": 1708363256
        },
        "id": "e62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43",
        "metadata": {
            "emitter_chain": 26,
            "prev_publish_time": 1708363256,
            "price_service_receive_time": 1708363256,
            "slot": 85480034
        },
        "price": {
            "conf": "509500001",
            "expo": -8,
            "price": "2920679499999",
            "publish_time": 1708363256
        },
        "vaa": "UE5BVQEAAAADuAEAAAADDQC1H7meY5fTed0FsykIb8dt+7nKpbuzfvU2DplDi+dcUl8MC+UIkS65+rkiq+zmNBxE2gaxkBkjdIicZ/fBo+X7AAEqp+WtlWb84np8jJfLpuQ2W+l5KXTigsdAhz5DyVgU3xs+EnaIZxBwcE7EKzjMam+V9rlRy0CGsiQ1kjqqLzfAAQLsoVO0Vu5gVmgc8XGQ7xYhoz36rsBgMjG+e3l/B01esQi/KzPuBf/Ar8Sg5aSEOvEU0muSDb+KIr6d8eEC+FtcAAPZEaBSt4ysXVL84LUcJemQD3SiG30kOfUpF8o7/wI2M2Jf/LyCsbKEQUyLtLbZqnJBSfZJR5AMsrnHDqngMLEGAAY4UDG9GCpRuPvg8hOlsrXuPP3zq7yVPqyG0SG+bNo8rEhP5b1vXlHdG4bZsutX47d5VZ6xnFROKudx3T3/fnWUAQgAU1+kUFc3e0ZZeX1dLRVEryNIVyxMQIcxWwdey+jlIAYowHRM0fJX3Scs80OnT/CERwh5LMlFyU1w578NqxW+AQl2E/9fxjgUTi8crOfDpwsUsmOWw0+Q5OUGhELv/2UZoHAjsaw9OinWUggKACo4SdpPlHYldoWF+J2yGWOW+F4iAQre4c+ocb6a9uSWOnTldFkioqhd9lhmV542+VonCvuy4Tu214NP+2UNd/4Kk3KJCf3iziQJrCBeLi1cLHdLUikgAQtvRFR/nepcF9legl+DywAkUHi5/1MNjlEQvlHyh2XbMiS85yu7/9LgM6Sr+0ukfZY5mSkOcvUkpHn+T+Nw/IrQAQ7lty5luvKUmBpI3ITxSmojJ1aJ0kj/dc0ZcQk+/qo0l0l3/eRLkYjw5j+MZKA8jEubrHzUCke98eSoj8l08+PGAA+DAKNtCwNZe4p6J1Ucod8Lo5RKFfA84CPLVyEzEPQFZ25U9grUK6ilF4GhEia/ndYXLBt3PGW3qa6CBBPM7rH3ABGAyYEtUwzB4CeVedA5o6cKpjRkIebqDNSOqltsr+w7kXdfFVtsK2FMGFZNt5rbpIR+ppztoJ6eOKHmKmi9nQ99ARKkTxRErOs9wJXNHaAuIRV38o1pxRrlQRzGsRuKBqxcQEpC8OPFpyKYcp6iD5l7cO/gRDTamLFyhiUBwKKMP07FAWTEJv8AAAAAABrhAfrtrFhR4yubI7X5QRqMK6xKrj7U3XuBHdGnLqSqcQAAAAAAGp0GAUFVV1YAAAAAAAUYUmIAACcQBsfKUtr4PgZbIXRxRESU79PjE4IBAFUA5i32yLSoX+GmfbRNwS3l2zMPesZrctxliv7fD0pBW0MAAAKqqMJFwAAAAAAqE/NX////+AAAAABkxCb7AAAAAGTEJvoAAAKqIcWxYAAAAAAlR5m4CP/mPsh1IezjYpDlJ4GRb5q4fTs2LjtyO6M0XgVimrIQ4kSh1qg7JKW4gbGkyRntVFR9JO/GNd3FPDit0BK6M+JzXh/h12YNCz9wxlZTvXrNtWNbzqT+91pvl5cphhSPMfAHyEzTPaGR9tKDy9KNu56pmhaY32d2vfEWQmKo22guegeR98oDxs67MmnUraco46a3zEnac2Bm80pasUgMO24="
    }

@pytest.fixture
def data_v2():
    return {
        "binary": {
            "encoding": "hex",
            "data": [
            "504e41550100000003b801000000030d014016474bab1868acfe943cdcd3cf7a8b7ccfaf6f2a31870694d11c441505d0552a42f57df50093df73eca16fad7ae3d768b0dd0e64dbaf71579fd5d05c46a5f20002098e46154c00ee17e878295edaca5decd18f7a1e9a1f0576ca090219f350118d1a4a0cc94b853c8ae1d5064439e719c953e61450745cf10086c37ec93d878b610003edf89d49fe5bb035d3cab5f3960ca5c7be37073b6680afb0f154ec684990923330f6db1fced4680dcfce8664c9d757fe2e8ca84aec8950004371ab794979db7101068a0231af6701f5fbfe55ac7dd31d640dd17f2fa92a10450d7a6e5db03c7c1f90131452ed1e3290fbbf00bc8528f616e81771460b2c307e02db811a84545180620107ab6ea34d72541f44cf34c8e919b9ef336eef9774ee4cf3d5c7cc71f5f90e49d23a05878e2e278402aff8217df84f9ce3ae782c389b3230d09e9e66fada355d6600084018b5993c68c4d616a570925e63a7c82c5444aee9a0f6153bd724e0755d3086374c9cf4e6ec2f08ab9c914b4cd3868e250ad4f946219cc2af0a31936cd38147000a079d8fb93db9c82263556dfd768b6173da40d35ea4691d21de59cf207381b5a05cb693fd4a75cb2b190c0270f2ddc14335adca66bcd5a634bf316a4385e97250010bf6dfa12e7820c58514c74ec21029d5c11f98a586743b2da9d2e20d8d78b44bd3730af5c6428c1ad865cb9d94ee795d059b3b51bb1e7bc8f81d52e5db18167648010c8558ac8aefd43cf489bce260afaee270d36fd1a34923439261fc8220cb33f30521cfefebfe0d7cf21d3aaa60c9149f8ab085c90b0509ad2850efe01fc618ccec010d6bc67036011a75277ca476ca1f4d962ca0d861805a94c6353ad0ff6ae17263bc5401e7d7ee3f3010f77c6349ff264c4185b167f32108c7de9743f7a258c62d03000e63f823f4b8f2cb1d158aac8f7ba0e45227b6d99106831a50729825bf8b97969503f55bc33778ef6c21e696a99d304b72c9e5ca3941dd178a7fc5367aed7d0e00010f22ccd76becc94aec99ff0bb1fce128cb25644268c65ac8f2bf5fe357910942381e184a62e8a768d5be200e21e40a34047a6e5cd981d2380de7eb4aa46a15ce0a00127957a07e69f8af6f8752a09f24dde0d43277c80d3bc24f09a281e5e68878d0ea0445b356257e25e80422ddff2f799bb732eafdeee43fc14c21d4eda349a547010165d38df800000000001ae101faedac5851e32b9b23b5f9411a8c2bac4aae3ed4dd7b811dd1a72ea4aa7100000000027a3abd0141555756000000000007823fd000002710b939e515de35dd00cf7feaba6be6aed77c83e09901005500e62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43000004b868a1a543000000009ea4861cfffffff80000000065d38df80000000065d38df7000004bcd90bec4000000000c41abcc80ab559eef775bd945c821d89ceba075f3c60f2dba713f2f7ed0d210ea03ee4bead9c9b6ffd8fff45f0826e6950c44a8a7e0eac9b5bc1f2bdf276965107fc612f72a05bd37ca85017dc13b01fa5d434887f33527d87c34f1caf4ed69501a6972959e7faf96a6bc43c0d08e2b1a095c50ef6609bf81b7661102f69acb46430115e301f1ebda0f008438e31564240e1cbc9092db20b73bfc8dd832b6467fd242f0043a167ccafbc0ba479d38be012ad1d75f35e2681754e78e1f10096a55f65512fe381238a67ffce0970"
            ]
        },
        "parsed": [
            {
                "id": "e62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43",
                "price": {
                    "price": "5190075917635",
                    "conf": "2661582364",
                    "expo": -8,
                    "publish_time": 1708363256
                },
                "ema_price": {
                    "price": "5209141800000",
                    "conf": "3290086600",
                    "expo": -8,
                    "publish_time": 1708363256
                },
                "metadata": {
                    "slot": 125976528,
                    "proof_available_time": 1708363257,
                    "prev_publish_time": 1708363255
                }
            }
        ]
    }

def test_parse_unsupported_version():
    with pytest.raises(ValueError):
        parse_unsupported_version(3)
    with pytest.raises(TypeError):
        parse_unsupported_version("3")

@pytest.fixture
def mock_get_price_feed_ids(mocker: MockerFixture):
    async_mock = AsyncMock()
    mocker.patch('pythclient.hermes.HermesClient.get_price_feed_ids', side_effect=async_mock)
    return async_mock

@pytest.mark.asyncio
async def test_hermes_add_feed_ids(hermes_client: HermesClient, mock_get_price_feed_ids: AsyncMock):
    mock_get_price_feed_ids.return_value = ["ff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace"]

    feed_ids = await hermes_client.get_price_feed_ids()

    feed_ids_pre = hermes_client.feed_ids
    pending_feed_ids_pre = hermes_client.pending_feed_ids

    # Add feed_ids to the client in duplicate
    for _ in range(3):
        hermes_client.add_feed_ids(feed_ids)

    assert len(set(hermes_client.feed_ids)) == len(hermes_client.feed_ids)
    assert set(hermes_client.feed_ids) == set(feed_ids_pre + feed_ids)
    assert set(hermes_client.pending_feed_ids) == set(pending_feed_ids_pre + feed_ids)

def test_hermes_extract_price_feed_v1(hermes_client: HermesClient, data_v1: dict):
    price_feed = hermes_client.extract_price_feed_v1(data_v1)

    assert isinstance(price_feed, dict)
    assert set(price_feed.keys()) == set(PriceFeed.__annotations__.keys())        
    
def test_hermes_extract_price_feed_v2(hermes_client: HermesClient, data_v2: dict):
    price_feed = hermes_client.extract_price_feed_v2(data_v2)

    assert isinstance(price_feed, list)
    assert isinstance(price_feed[0], dict)
    assert set(price_feed[0].keys()) == set(PriceFeed.__annotations__.keys())
