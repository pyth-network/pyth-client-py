from typing import Optional

from loguru import logger

DEFAULT_VERSION = "v2"


# Retrieving keys via DNS TXT records should not be considered secure and is provided as a convenience only.
# Accounts should be stored locally and verified before being used for production.
def get_key(network: str, type: str) -> Optional[str]:
    """
    Get the program or mapping key.
    :param network: The network to get the key for. Either "mainnet", "devnet", "testnet", "pythnet", "pythtest-conformance", or "pythtest-crosschain".
    :param type: The type of key to get. Either "program" or "mapping".
    """
    if network == "pythnet":
        program_key = "FsJ3A3u2vn5cTVofAjvy6y5kwABJAqYWpe4975bi2epH"
        mapping_key = "AHtgzX45WTKfkPG53L6WYhGEXwQkN1BVknET3sVsLL8J"
    elif network == "mainnet":
        program_key = "FsJ3A3u2vn5cTVofAjvy6y5kwABJAqYWpe4975bi2epH"
        mapping_key = "AHtgzX45WTKfkPG53L6WYhGEXwQkN1BVknET3sVsLL8J"
    elif network == "devnet":
        program_key = "gSbePebfvPy7tRqimPoVecS2UsBvYv46ynrzWocc92s"
        mapping_key = "BmA9Z6FjioHJPpjT39QazZyhDRUdZy2ezwx4GiDdE2u2"
    elif network == "testnet":
        program_key = "8tfDNiaEyrV6Q1U4DEXrEigs9DoDtkugzFbybENEbCDz"
        mapping_key = "AFmdnt9ng1uVxqCmqwQJDAYC5cKTkw8gJKSM5PnzuF6z"
    elif network == "pythtest-conformance":
        program_key = "8tfDNiaEyrV6Q1U4DEXrEigs9DoDtkugzFbybENEbCDz"
        mapping_key = "AFmdnt9ng1uVxqCmqwQJDAYC5cKTkw8gJKSM5PnzuF6z"
    elif network == "pythtest-crosschain":
        program_key = "gSbePebfvPy7tRqimPoVecS2UsBvYv46ynrzWocc92s"
        mapping_key = "BmA9Z6FjioHJPpjT39QazZyhDRUdZy2ezwx4GiDdE2u2"
    else:
        raise Exception(f"Unknown network: {network}")

    if type == "program":
        return program_key
    elif type == "mapping":
        return mapping_key
    else:
        raise Exception(f"Unknown type: {type}")
