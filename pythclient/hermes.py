import asyncio
from typing import TypedDict
import httpx
import os
import json
import websockets

from .price_feeds import Price

HERMES_ENDPOINT_HTTPS = "https://hermes.pyth.network/"
HERMES_ENDPOINT_WSS = "wss://hermes.pyth.network/ws"


class PriceFeed(TypedDict):
    feed_id: str
    price: Price
    ema_price: Price
    update_data: list[str]


def parse_unsupported_version(version):
    if isinstance(version, int):
        raise ValueError("Version number {version} not supported")
    else:
        raise TypeError("Version must be an integer")


class HermesClient:
    def __init__(self, feed_ids: list[str], endpoint=HERMES_ENDPOINT_HTTPS, ws_endpoint=HERMES_ENDPOINT_WSS, feed_batch_size=100):
        self.feed_ids = feed_ids
        self.pending_feed_ids = feed_ids
        self.prices_dict: dict[str, PriceFeed] = {}
        self.endpoint = endpoint
        self.ws_endpoint = ws_endpoint
        self.feed_batch_size = feed_batch_size # max number of feed IDs to query at once in https requests

    async def get_price_feed_ids(self) -> list[str]:
        """
        Queries the Hermes https endpoint for a list of the IDs of all Pyth price feeds.
        """

        url = os.path.join(self.endpoint, "api/price_feed_ids")

        async with httpx.AsyncClient() as client:
            data = (await client.get(url)).json()

        return data

    def add_feed_ids(self, feed_ids: list[str]):
        # convert feed_ids to a set to remove any duplicates from the input
        new_feed_ids_set = set(feed_ids)
        
        # update self.feed_ids; convert to set for union operation, then back to list
        self.feed_ids = list(set(self.feed_ids).union(new_feed_ids_set))
        
        # update self.pending_feed_ids with only those IDs that are truly new
        self.pending_feed_ids = list(set(self.pending_feed_ids).union(new_feed_ids_set))

    @staticmethod
    def extract_price_feed_v1(data: dict) -> PriceFeed:
        """
        Extracts PriceFeed object from the v1 JSON response (individual price feed) from Hermes.
        """
        price = Price.from_dict(data["price"])
        ema_price = Price.from_dict(data["ema_price"])
        update_data = data["vaa"]
        price_feed = {
            "feed_id": data["id"],
            "price": price,
            "ema_price": ema_price,
            "update_data": [update_data],
        }
        return price_feed
    
    @staticmethod
    def extract_price_feed_v2(data: dict) -> list[PriceFeed]:
        """
        Extracts PriceFeed objects from the v2 JSON response (array of price feeds) from Hermes.
        """
        update_data = data["binary"]["data"]

        price_feeds = []

        for feed in data["parsed"]:
            price = Price.from_dict(feed["price"])
            ema_price = Price.from_dict(feed["ema_price"])
            price_feed = {
                "feed_id": feed["id"],
                "price": price,
                "ema_price": ema_price,
                "update_data": update_data,
            }
            price_feeds.append(price_feed)

        return price_feeds

    async def get_pyth_prices_latest(self, feedIds: list[str], version=2) -> list[PriceFeed]:
        """
        Queries the Hermes https endpoint for the latest price feeds for a list of Pyth feed IDs.
        """
        if version==1:
            url = os.path.join(self.endpoint, "api/latest_price_feeds")
            params = {"ids[]": feedIds, "binary": "true"}
        elif version==2:
            url = os.path.join(self.endpoint, "v2/updates/price/latest")
            params = {"ids[]": feedIds, "encoding": "base64", "parsed": "true"}
        else:
            parse_unsupported_version(version)

        async with httpx.AsyncClient() as client:
            data = (await client.get(url, params=params)).json()

        if version==1:
            results = []
            for res in data:
                price_feed = self.extract_price_feed_v1(res)
                results.append(price_feed)
        elif version==2:
            results = self.extract_price_feed_v2(data)

        return results

    async def get_pyth_price_at_time(self, feed_id: str, timestamp: int, version=2) -> PriceFeed:
        """
        Queries the Hermes https endpoint for the price feed for a Pyth feed ID at a given timestamp.
        """
        if version==1:
            url = os.path.join(self.endpoint, "api/get_price_feed")
            params = {"id": feed_id, "publish_time": timestamp, "binary": "true"}
        elif version==2:
            url = os.path.join(self.endpoint, f"v2/updates/price/{timestamp}")
            params = {"ids[]": [feed_id], "encoding": "base64", "parsed": "true"}
        else:
            parse_unsupported_version(version)

        async with httpx.AsyncClient() as client:
            data = (await client.get(url, params=params)).json()

        if version==1:
            price_feed = self.extract_price_feed_v1(data)
        elif version==2:
            price_feed = self.extract_price_feed_v2(data)[0]

        return price_feed

    async def get_all_prices(self, version=2) -> dict[str, PriceFeed]:
        """
        Queries the Hermes http endpoint for the latest price feeds for all feed IDs in the class object.

        There is a limit on the number of feed IDs that can be queried at once, so this function queries the feed IDs in batches.
        """
        pyth_prices_latest = []
        i = 0
        while len(self.feed_ids[i : i + self.feed_batch_size]) > 0:
            pyth_prices_latest += await self.get_pyth_prices_latest(
                self.feed_ids[i : i + self.feed_batch_size],
                version=version,
            )
            i += self.feed_batch_size

        return dict([(feed['feed_id'], feed) for feed in pyth_prices_latest])

    async def ws_pyth_prices(self, version=1):
        """
        Opens a websocket connection to Hermes for latest prices for all feed IDs in the class object.
        """
        if version != 1:
            parse_unsupported_version(version)
        
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

                    self.prices_dict[feed_id] = self.extract_price_feed_v1(new_feed)

                except Exception as e:
                    raise Exception(f"Error in price_update message: {msg}") from e