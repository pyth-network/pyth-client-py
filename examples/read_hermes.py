#!/usr/bin/env python3

import asyncio

from pythclient.hermes import HermesClient

async def get_hermes_prices():
    hermes_client = HermesClient([])
    feed_ids = await hermes_client.get_price_feed_ids()
    feed_ids_rel = feed_ids[:2]
    version_http = 1
    version_ws = 1

    hermes_client.add_feed_ids(feed_ids_rel)

    prices_latest = await hermes_client.get_all_prices(version=version_http)

    for feed_id, price_feed in prices_latest.items():
        print("Initial prices")
        print(f"Feed ID: {feed_id}, Price: {price_feed['price'].price}, Confidence: {price_feed['price'].conf}, Time: {price_feed['price'].publish_time}")

    print("Starting web socket...")
    ws_call = hermes_client.ws_pyth_prices(version=version_ws)
    ws_task = asyncio.create_task(ws_call)

    while True:
        await asyncio.sleep(5)
        if ws_task.done():
            break
        print("Latest prices:")
        for feed_id, price_feed in hermes_client.prices_dict.items():
            print(f"Feed ID: {feed_id}, Price: {price_feed['price'].price}, Confidence: {price_feed['price'].conf}, Time: {price_feed['price'].publish_time}")

asyncio.run(get_hermes_prices())
