import asyncio
from typing import TypedDict

import httpx
import os

from .price_feeds import Price

HERMES_ENDPOINT_HTTPS = "https://hermes.pyth.network/api/"
HERMES_ENDPOINT_WSS = "wss://hermes.pyth.network/ws"


class PriceFeed(TypedDict):
    feed_id: str
    price: Price
    ema_price: Price
    vaa: str



class HermesClient:
    def __init__(self, feed_ids: list[str], endpoint=HERMES_ENDPOINT_HTTPS, ws_endpoint=HERMES_ENDPOINT_WSS):
        self.feed_ids = feed_ids
        self.pending_feed_ids = feed_ids
        self.prices_dict: dict[str, PriceFeed] = {}
        self.client = httpx.AsyncClient()
        self.endpoint = endpoint
        self.ws_endpoint = ws_endpoint

    async def get_price_feed_ids(self) -> list[str]:
        """
        Queries the Hermes https endpoint for a list of the IDs of all Pyth price feeds.
        """

        url = os.path.join(self.endpoint, "price_feed_ids")
        
        client = httpx.AsyncClient()

        data = (await client.get(url)).json()

        return data

    def add_feed_ids(self, feed_ids: list[str]):
        self.feed_ids += feed_ids
        self.feed_ids = list(set(self.feed_ids))
        self.pending_feed_ids += feed_ids

    @staticmethod
    def extract_price_feed(data: dict) -> PriceFeed:
        """
        Extracts a PriceFeed object from the JSON response from Hermes.
        """
        price = Price.from_dict(data["price"])
        ema_price = Price.from_dict(data["ema_price"])
        vaa = data["vaa"]
        price_feed = {
            "feed_id": data["id"],
            "price": price,
            "ema_price": ema_price,
            "vaa": vaa,
        }
        return price_feed

    async def get_pyth_prices_latest(self, feedIds: list[str]) -> list[PriceFeed]:
        """
        Queries the Hermes https endpoint for the latest price feeds for a list of Pyth feed IDs.
        """
        url = os.path.join(self.endpoint, "latest_price_feeds?")
        params = {"ids[]": feedIds, "binary": "true"}

        data = (await self.client.get(url, params=params)).json()

        results = []
        for res in data:
            price_feed = self.extract_price_feed(res)
            results.append(price_feed)

        return results

    async def get_pyth_price_at_time(self, feed_id: str, timestamp: int) -> PriceFeed:
        """
        Queries the Hermes https endpoint for the price feed for a Pyth feed ID at a given timestamp.
        """
        url = os.path.join(self.endpoint, "get_price_feed")
        params = {"id": feed_id, "publish_time": timestamp, "binary": "true"}

        data = (await self.client.get(url, params=params)).json()

        price_feed = self.extract_price_feed(data)

        return price_feed

    async def get_all_prices(self) -> dict[str, PriceFeed]:
        """
        Queries the Hermes http endpoint for the latest price feeds for all feed IDs in the class object.

        There are limitations on the number of feed IDs that can be queried at once, so this function queries the feed IDs in batches.
        """
        pyth_prices_latest = []
        i = 0
        batch_size = 100
        while len(self.feed_ids[i : i + batch_size]) > 0:
            pyth_prices_latest += await self.get_pyth_prices_latest(
                self.feed_ids[i : i + batch_size]
            )
            i += batch_size

        return dict([(feed['feed_id'], feed) for feed in pyth_prices_latest])

    async def ws_pyth_prices(self):
        """
        Opens a websocket connection to Hermes for latest prices for all feed IDs in the class object.
        """
        import json

        import websockets

        async with websockets.connect(self.ws_endpoint) as ws:
            while True:
                # add new price feed ids to the ws subscription
                if len(self.pending_feed_ids) > 0:
                    json_subscribe = {
                        "ids": self.pending_feed_ids,
                        "type": "subscribe",
                        "verbose": True,
                        "binary": True,
                    }
                    await ws.send(json.dumps(json_subscribe))
                    self.pending_feed_ids = []

                msg = json.loads(await ws.recv())
                if msg.get("type") == "response":
                    if msg.get("status") != "success":
                        raise Exception("Error in subscribing to websocket")
                try:
                    if msg["type"] != "price_update":
                        continue

                    feed_id = msg["price_feed"]["id"]
                    new_feed = msg["price_feed"]

                    self.prices_dict[feed_id] = self.extract_price_feed(new_feed)

                except:
                    raise Exception("Error in price_update message", msg)


async def main():
    hermes_client = HermesClient([])
    feed_ids = await hermes_client.get_price_feed_ids()
    feed_ids_rel = feed_ids[:50]

    hermes_client.add_feed_ids(feed_ids_rel)

    prices_latest = await hermes_client.get_pyth_prices_latest(feed_ids_rel)

    try:
        price_at_time = await hermes_client.get_pyth_price_at_time(feed_ids[0], 1_700_000_000)
    except Exception as e:
        print(f"Error in get_pyth_price_at_time, {e}")

    all_prices = await hermes_client.get_all_prices()

    print("Starting web socket...")
    ws_call = hermes_client.ws_pyth_prices()
    asyncio.create_task(ws_call)

    while True:
        await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())
