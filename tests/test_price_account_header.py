import pytest

from pythclient.pythaccounts import PythAccountType, _parse_header


@pytest.fixture
def valid_binary():
    """
    magic=0xA1B2C3D4 version=2, type=price, size=16
    """
    return bytes([212, 195, 178, 161, 2, 0, 0, 0, 3, 0, 0, 0, 16, 0, 0, 0])


@pytest.fixture
def valid_expected():
    return PythAccountType.PRICE, 16, 2


@pytest.fixture
def bad_magic():
    """
    magic=0xDEADBEEF, version=2, type=price, size=16
    """
    return bytes([239, 190, 173, 222, 2, 0, 0, 0, 3, 0, 0, 0, 16, 0, 0, 0])


@pytest.fixture
def bad_magic_message():
    return "Invalid Pyth account data header has wrong magic: expected a1b2c3d4, got deadbeef"


@pytest.fixture
def wrong_version():
    """
    magic=0xA1B2C3D4 version=42, type=price, size=16
    """
    return bytes([212, 195, 178, 161, 42, 0, 0, 0, 3, 0, 0, 0, 16, 0, 0, 0])


@pytest.fixture
def wrong_version_message():
    return "Invalid Pyth account data has unsupported version 42"


@pytest.fixture
def wrong_size():
    """
    magic=0xA1B2C3D4 version=2, type=price, size=32
    """
    return bytes([212, 195, 178, 161, 2, 0, 0, 0, 3, 0, 0, 0, 32, 0, 0, 0])


@pytest.fixture
def wrong_size_message():
    return "Invalid Pyth header says data is 32 bytes, but buffer only has 16 bytes"


@pytest.fixture
def too_short():
    """
    Totally bogus messge that is too short
    """
    return bytes([1, 2, 3, 4])


@pytest.fixture
def too_short_message():
    return "Pyth account data too short"


@pytest.mark.parametrize(
        "buffer_fixture_name",
        ["bad_magic", "wrong_version", "wrong_size", "too_short"],
)
def test_header_parsing_errors(buffer_fixture_name, request):
    buffer = request.getfixturevalue(buffer_fixture_name)
    exc_message = request.getfixturevalue(f"{buffer_fixture_name}_message")

    with pytest.raises(ValueError, match=exc_message):
        _parse_header(
            buffer=buffer,
            offset=0,
            key="Invalid",
        )


def test_header_parsing_valid(valid_binary, valid_expected):
    actual = _parse_header(
        buffer=valid_binary,
        offset=0,
        key="Invalid",
    )
    assert actual == valid_expected
