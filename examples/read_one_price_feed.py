#!/usr/bin/env python3

import asyncio

from pythclient.pythaccounts import PythPriceAccount
from pythclient.solana import SolanaClient, SolanaPublicKey, SOLANA_DEVNET_HTTP_ENDPOINT, SOLANA_DEVNET_WS_ENDPOINT

async def get_price():
    # devnet DOGE/USD price account key (available on pyth.network website)
    account_key = SolanaPublicKey("4L6YhY8VvUgmqG5MvJkUJATtzB2rFqdrJwQCmFLv4Jzy")
    solana_client = SolanaClient(endpoint=SOLANA_DEVNET_HTTP_ENDPOINT, ws_endpoint=SOLANA_DEVNET_WS_ENDPOINT)
    price: PythPriceAccount = PythPriceAccount(account_key, solana_client)

    await price.update()
    # Sample output: "DOGE/USD is 0.141455 ± 7.4e-05"
    print("DOGE/USD is", price.aggregate_price, "±", price.aggregate_price_confidence_interval)

asyncio.run(get_price())
