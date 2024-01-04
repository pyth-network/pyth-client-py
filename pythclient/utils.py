from typing import Optional


def get_key(network: str, type: str) -> Optional[str]:
    """
    Get the program or mapping key.
    :param network: The network to get the key for. Either "mainnet", "devnet", "testnet", "pythnet", "pythtest-conformance", or "pythtest-crosschain".
    :param type: The type of key to get. Either "program" or "mapping".
    """
    keys = {
        "pythnet": {
            "program": "FsJ3A3u2vn5cTVofAjvy6y5kwABJAqYWpe4975bi2epH",
            "mapping": "AHtgzX45WTKfkPG53L6WYhGEXwQkN1BVknET3sVsLL8J",
        },
        "mainnet": {
            "program": "FsJ3A3u2vn5cTVofAjvy6y5kwABJAqYWpe4975bi2epH",
            "mapping": "AHtgzX45WTKfkPG53L6WYhGEXwQkN1BVknET3sVsLL8J",
        },
        "devnet": {
            "program": "gSbePebfvPy7tRqimPoVecS2UsBvYv46ynrzWocc92s",
            "mapping": "BmA9Z6FjioHJPpjT39QazZyhDRUdZy2ezwx4GiDdE2u2",
        },
        "testnet": {
            "program": "8tfDNiaEyrV6Q1U4DEXrEigs9DoDtkugzFbybENEbCDz",
            "mapping": "AFmdnt9ng1uVxqCmqwQJDAYC5cKTkw8gJKSM5PnzuF6z",
        },
        "pythtest-conformance": {
            "program": "8tfDNiaEyrV6Q1U4DEXrEigs9DoDtkugzFbybENEbCDz",
            "mapping": "AFmdnt9ng1uVxqCmqwQJDAYC5cKTkw8gJKSM5PnzuF6z",
        },
        "pythtest-crosschain": {
            "program": "gSbePebfvPy7tRqimPoVecS2UsBvYv46ynrzWocc92s",
            "mapping": "BmA9Z6FjioHJPpjT39QazZyhDRUdZy2ezwx4GiDdE2u2",
        },
    }

    try:
        return keys[network][type]
    except KeyError:
        raise Exception(f"Unknown network or type: {network}, {type}")
