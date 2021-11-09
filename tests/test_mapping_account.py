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

        print(list(product_account_bytes))

    """
    return bytes(
        [
            3, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0,
            72, 214, 3, 61, 115, 62, 39, 149, 12, 46, 3, 81, 226, 80,
            84, 145, 205, 145, 84, 130, 79, 113, 109, 149, 19, 81, 76,
            116, 185, 249, 143, 88, 200, 12, 11, 20, 138, 186, 153, 75,
            37, 102, 234, 84, 167, 143, 240, 142, 250, 61, 94, 14, 195,
            208, 206, 234, 12, 250, 160, 63, 236, 37, 238, 162, 53, 21,
            179, 134, 30, 143, 233, 62, 95, 84, 11, 164, 7, 124, 33,
            100, 4, 120, 43, 134, 213, 231, 128, 119, 179, 203, 253,
            39, 49, 58, 179, 188
        ]
    )


@pytest.fixture
def entries():
    return [
        SolanaPublicKey("5uKdRzB3FzdmwyCHrqSGq4u2URja617jqtKkM71BVrkw"),
        SolanaPublicKey("ETuC4VK6kuHfxc9MCU14dASfnGBfzgFUVCs1oVowawHb"),
        SolanaPublicKey("4aDoSXJ5o3AuvL7QFeR6h44jALQfTmUUCTVGDD6aoJTM"),
    ]


@pytest.fixture
def mapping_key():
    return SolanaPublicKey("AHtgzX45WTKfkPG53L6WYhGEXwQkN1BVknET3sVsLL8J")


def test_mapping_account_upate_from(
    solana_client, mapping_key, mapping_account_bytes, entries
):
    account = PythMappingAccount(
        key=mapping_key,
        solana=solana_client,
    )
    assert account.entries == []
    assert account.next_account_key is None

    account.update_from(
        buffer=mapping_account_bytes,
        version=_VERSION_2,
        offset=0,
    )

    assert account.entries == entries
    assert account.next_account_key is None


def test_mapping_account_upate_from_null_key(
    solana_client, mapping_key, mapping_account_bytes, entries
):
    account = PythMappingAccount(
        key=mapping_key,
        solana=solana_client,
    )
    assert account.entries == []
    assert account.next_account_key is None

    # Replace the last key with a null key
    null_key_bytes = b"\0" * SolanaPublicKey.LENGTH

    # Length of bytes with the last pubkey trimmed
    offset = len(mapping_account_bytes) - SolanaPublicKey.LENGTH

    # Take the original bytes and add a null key to the end
    bad_bytes = mapping_account_bytes[:offset] + null_key_bytes

    account.update_from(
        buffer=bad_bytes,
        version=_VERSION_2,
        offset=0,
    )

    # The last key in the list is null, so remove it
    expected = entries[: len(entries) - 1]

    assert account.entries == expected
    assert account.next_account_key is None


def test_mapping_account_str(mapping_key, solana_client):
    actual = str(
        PythMappingAccount(
            key=mapping_key,
            solana=solana_client,
        )
    )
    expected = f"PythMappingAccount ({mapping_key})"
    assert actual == expected
