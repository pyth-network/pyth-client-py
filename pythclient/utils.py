import ast
import dns.resolver
from loguru import logger
from typing import Optional

DEFAULT_VERSION = "v2"


# Retrieving keys via DNS TXT records should not be considered secure and is provided as a convenience only.
# Accounts should be stored locally and verified before being used for production.
def get_key(network: str, type: str, version: str = DEFAULT_VERSION) -> Optional[str]:
    """
    Get the program or mapping keys from dns TXT records.

    Example dns records:

        devnet-program-v2.pyth.network
        mainnet-program-v2.pyth.network
        testnet-mapping-v2.pyth.network
    """
    url = f"{network}-{type}-{version}.pyth.network"
    try:
        answer = dns.resolver.resolve(url, "TXT")
    except dns.resolver.NXDOMAIN:
        logger.error("TXT record for {} not found", url)
        return ""
    if len(answer) != 1:
        logger.error("Invalid number of records returned for {}!", url)
        return ""
    # Example of the raw_key:
    #     "program=FsJ3A3u2vn5cTVofAjvy6y5kwABJAqYWpe4975bi2epH"
    raw_key = ast.literal_eval(list(answer)[0].to_text())
    # program=FsJ3A3u2vn5cTVofAjvy6y5kwABJAqYWpe4975bi2epH"
    _, key = raw_key.split("=", 1)
    return key
