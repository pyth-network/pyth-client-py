#!/usr/bin/env python3

from __future__ import annotations
import asyncio
import os
import signal
import sys
from typing import List, Any

from loguru import logger

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from pythclient.pythclient import PythClient, V2_PROGRAM_KEY, V2_FIRST_MAPPING_ACCOUNT_KEY
from pythclient.ratelimit import RateLimit
from pythclient.pythaccounts import PythPriceAccount

logger.enable("pythclient")

RateLimit.configure_default_ratelimit(overall_cps=9, method_cps=3, connection_cps=3)

to_exit = False


def set_to_exit(sig: Any, frame: Any):
    global to_exit
    to_exit = True


signal.signal(signal.SIGINT, set_to_exit)


async def main():
    global to_exit
    use_program = len(sys.argv) >= 2 and sys.argv[1] == "program"
    async with PythClient(first_mapping_account_key=V2_FIRST_MAPPING_ACCOUNT_KEY, program_key=V2_PROGRAM_KEY if use_program else None) as c:
        await c.refresh_all_prices()
        products = await c.get_products()
        all_prices: List[PythPriceAccount] = []
        for p in products:
            print(p.key, p.attrs)
            prices = await p.get_prices()
            for _, pr in prices.items():
                all_prices.append(pr)
                print(
                    pr.key,
                    pr.product_account_key,
                    pr.price_type,
                    pr.aggregate_price,
                    "p/m",
                    pr.aggregate_price_confidence_interval,
                )

        ws = c.create_watch_session()
        await ws.connect()
        if use_program:
            print("Subscribing to program account")
            await ws.program_subscribe(V2_PROGRAM_KEY, await c.get_all_accounts())
        else:
            print("Subscribing to all prices")
            for account in all_prices:
                await ws.subscribe(account)
        print("Subscribed!")

        while True:
            if to_exit:
                break
            update_task = asyncio.create_task(ws.next_update())
            while True:
                if to_exit:
                    update_task.cancel()
                    break
                done, _ = await asyncio.wait({update_task}, timeout=1)
                if update_task in done:
                    pr = update_task.result()
                    if isinstance(pr, PythPriceAccount):
                        assert pr.product
                        print(
                            pr.product.symbol,
                            pr.price_type,
                            pr.aggregate_price,
                            "p/m",
                            pr.aggregate_price_confidence_interval,
                        )
                        break
                    else:
                        print("WTF!: ", price)

        print("Unsubscribing...")
        if use_program:
            await ws.program_unsubscribe(V2_PROGRAM_KEY)
        else:
            for account in all_prices:
                await ws.unsubscribe(account)
        await ws.disconnect()
        print("Disconnected")


asyncio.run(main())
