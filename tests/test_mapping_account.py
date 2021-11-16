import base64
import pytest

from pythclient.pythaccounts import PythMappingAccount, _VERSION_2
from pythclient.solana import SolanaPublicKey


@pytest.fixture
def mapping_account_bytes():
    """
    Put a debugger breakpoint in PythMappingAccount.update_from() at the top.
    Get the mapping account number of entries and 3 keys:

        fmt_size = struct.calcsize(fmt)
        intermediate_buffer = buffer[offset:offset + fmt_size + (SolanaPublicKey.LENGTH * 3)]

    Replace the num_keys bytes with 3:

        num_entries_bytes = int(3).to_bytes(4, 'little')
        product_account_bytes = num_entries_bytes + intermediate_buffer[struct.calcsize("<I"):]

    Render those into a pasteable form with:

        print(base64.b6encode(product_account_bytes))

    """
    return base64.b64decode((
        b'AwAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAEjWAz1zPieVDC4DUeJQVJHNkVSCT3FtlRNRT'
        b'HS5+Y9YyAwLFIq6mUslZupUp4/wjvo9Xg7D0M7qDPqgP+wl7qI1FbOGHo/pPl9UC6QHfCFkBHgrhtXngHezy/0nMT'
        b'qzvA=='
    ))


@pytest.fixture
def entries():
    return [
        SolanaPublicKey("5uKdRzB3FzdmwyCHrqSGq4u2URja617jqtKkM71BVrkw"),
        SolanaPublicKey("ETuC4VK6kuHfxc9MCU14dASfnGBfzgFUVCs1oVowawHb"),
        SolanaPublicKey("4aDoSXJ5o3AuvL7QFeR6h44jALQfTmUUCTVGDD6aoJTM"),
    ]


@pytest.fixture
def mapping_account(solana_client):
    return PythMappingAccount(
        key=SolanaPublicKey("AHtgzX45WTKfkPG53L6WYhGEXwQkN1BVknET3sVsLL8J"),
        solana=solana_client,
    )


def test_mapping_account_update_from(
    solana_client, mapping_account, mapping_account_bytes, entries
):
    mapping_account.update_from(
        buffer=mapping_account_bytes,
        version=_VERSION_2,
        offset=0,
    )

    assert mapping_account.entries == entries
    assert mapping_account.next_account_key is None


def test_mapping_account_upate_from_null_key(
    solana_client, mapping_account, mapping_account_bytes, entries
):
    # Replace the last key with a null key
    null_key_bytes = b"\0" * SolanaPublicKey.LENGTH

    # Length of bytes with the last pubkey trimmed
    offset = len(mapping_account_bytes) - SolanaPublicKey.LENGTH

    # Take the original bytes and add a null key to the end
    bad_bytes = mapping_account_bytes[:offset] + null_key_bytes

    mapping_account.update_from(
        buffer=bad_bytes,
        version=_VERSION_2,
        offset=0,
    )

    # The last key in the list is null, so remove it
    expected = entries[:-1]

    assert mapping_account.entries == expected
    assert mapping_account.next_account_key is None


def test_mapping_account_str(mapping_account, solana_client):
    actual = str(mapping_account)
    expected = f"PythMappingAccount ({mapping_account.key})"
    assert actual == expected
