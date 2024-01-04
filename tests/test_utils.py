import pytest

from pythclient.utils import get_key


def test_utils_get_program_key() -> None:
    program_key = get_key("devnet", "program")
    assert program_key == "gSbePebfvPy7tRqimPoVecS2UsBvYv46ynrzWocc92s"


def test_utils_get_mapping_key() -> None:
    mapping_key = get_key("devnet", "mapping")
    assert mapping_key == "BmA9Z6FjioHJPpjT39QazZyhDRUdZy2ezwx4GiDdE2u2"


def test_utils_invalid_network() -> None:
    with pytest.raises(Exception) as e:
        get_key("testdevnet", "mapping")
    assert str(e.value) == "Unknown network or type: testdevnet, mapping"


def test_utils_get_invalid_type() -> None:
    with pytest.raises(Exception) as e:
        get_key("devnet", "mappingprogram")
    assert str(e.value) == "Unknown network or type: devnet, mappingprogram"
