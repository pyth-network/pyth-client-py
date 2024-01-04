from __future__ import annotations
from typing import Union, Optional, Dict, List, Any, Sequence, cast
from typing_extensions import Literal
import asyncio
import json

import aiohttp
import backoff
import base58
from loguru import logger

from .exceptions import RateLimitedException, SolanaException, WebSocketClosedException
from .ratelimit import RateLimit
from . import config

WS_PREFIX = "wss"
HTTP_PREFIX = "https"

DEVNET_ENDPOINT = "api.devnet.solana.com"
TESTNET_ENDPOINT = "api.testnet.solana.com"
MAINNET_ENDPOINT = "api.mainnet-beta.solana.com"
PYTHNET_ENDPOINT = "pythnet.rpcpool.com"
PYTHTEST_CROSSCHAIN_ENDPOINT = "api.pythtest.pyth.network"
PYTHTEST_CONFORMANCE_ENDPOINT = "api.pythtest.pyth.network"

SOLANA_DEVNET_WS_ENDPOINT = WS_PREFIX + "://" + DEVNET_ENDPOINT
SOLANA_DEVNET_HTTP_ENDPOINT = HTTP_PREFIX + "://" + DEVNET_ENDPOINT

SOLANA_TESTNET_WS_ENDPOINT = WS_PREFIX + "://" + TESTNET_ENDPOINT
SOLANA_TESTNET_HTTP_ENDPOINT = HTTP_PREFIX + "://" + TESTNET_ENDPOINT

SOLANA_MAINNET_WS_ENDPOINT = WS_PREFIX + "://" + MAINNET_ENDPOINT
SOLANA_MAINNET_HTTP_ENDPOINT = HTTP_PREFIX + "://" + MAINNET_ENDPOINT

PYTHNET_WS_ENDPOINT = WS_PREFIX + "://" + PYTHNET_ENDPOINT
PYTHNET_HTTP_ENDPOINT = HTTP_PREFIX + "://" + PYTHNET_ENDPOINT

PYTHTEST_CROSSCHAIN_WS_ENDPOINT = WS_PREFIX + "://" + PYTHTEST_CROSSCHAIN_ENDPOINT
PYTHTEST_CROSSCHAIN_HTTP_ENDPOINT = HTTP_PREFIX + "://" + PYTHTEST_CROSSCHAIN_ENDPOINT

PYTHTEST_CONFORMANCE_WS_ENDPOINT = WS_PREFIX + "://" + PYTHTEST_CONFORMANCE_ENDPOINT
PYTHTEST_CONFORMANCE_HTTP_ENDPOINT = HTTP_PREFIX + "://" + PYTHTEST_CONFORMANCE_ENDPOINT

class SolanaPublicKey:
    """
    Represents a Solana public key. This class is meant to be immutable.
    """

    LENGTH = 32
    NULL_KEY: SolanaPublicKey

    def __init__(self, key: Union[str, bytes]):
        """
        Constructs a new SolanaPublicKey, either from a base58-encoded str or a raw 32-byte bytes.
        """
        if isinstance(key, str):
            b58len = len(base58.b58decode(key))
            if b58len != SolanaPublicKey.LENGTH:
                raise ValueError(
                    f"invalid byte length of key, expected {SolanaPublicKey.LENGTH}, got {b58len}"
                )
            self.key = key
        elif isinstance(key, bytes): # type: ignore  # suppress unnecessaryIsInstance here
            if len(key) != SolanaPublicKey.LENGTH:
                raise ValueError(
                    f"invalid byte length of key, expected {SolanaPublicKey.LENGTH}, got {len(key)}"
                )
            self.key = base58.b58encode(key).decode("utf-8")
        else:
            raise ValueError(f"expected str or bytes for key, got {type(key)}")

    def __str__(self):
        return self.key

    def __repr__(self):
        return str(self)

    # __hash__ and __eq__ simply pass through to self.key (str). this is present
    # so that SolanaPublicKey can be used as a dictionary key and so that equality
    # works as expected (i.e. SolanaPublicKey("abc") == SolanaPublicKey("abc"))
    def __hash__(self):
        return self.key.__hash__()

    def __eq__(self, other: Any):
        return isinstance(other, SolanaPublicKey) and self.key.__eq__(other.key)


SolanaPublicKeyOrStr = Union[SolanaPublicKey, str]
SolanaPublicKey.NULL_KEY = SolanaPublicKey(b'\0' * 32)


class SolanaAccount:
    """
    Represents a Solana account.

    Attributes:
        key (SolanaPublicKey): the public key of this account
        slot (Optional[int]): the slot time when the data in this account was
            last updated
        solana (SolanaClient): the Solana RPC client
        lamports (Optional[int]): the account's balance, in lamports
    """

    def __init__(self, key: SolanaPublicKeyOrStr, solana: SolanaClient) -> None:
        self.key: SolanaPublicKey = key if isinstance(key, SolanaPublicKey) else SolanaPublicKey(key)
        self.solana: SolanaClient = solana
        self.slot: Optional[int] = None
        self.lamports: Optional[int] = None

    def update_with_rpc_response(self, slot: int, value: Dict[str, Any]) -> None:
        """
        Update the data in this object from the given JSON RPC response from the
        Solana node.
        """
        self.slot = slot
        self.lamports: Optional[int] = value.get("lamports")

    async def update(self) -> None:
        """
        Update the data in this object by retrieving new account data from the
        Solana blockchain.
        """
        resp = await self.solana.get_account_info(self.key)
        value = resp.get("value")
        if value:
            try:
                self.update_with_rpc_response(resp["context"]["slot"], value)
            except Exception as ex:
                logger.exception("error while updating account {}", self.key, exception=ex)
        else:
            logger.warning("got null value from Solana getAccountInfo for {}; non-existent account? {}", self.key, resp)

    def __str__(self) -> str:
        return f"SolanaAccount ({self.key})"


class SolanaCommitment:
    FINALIZED = "finalized"
    CONFIRMED = "confirmed"
    PROCESSED = "processed"


class SolanaClient:
    def __init__(
        self,
        ratelimit: Union[Literal[False], RateLimit, None] = None,
        client: Optional[aiohttp.ClientSession] = None,
        *,
        endpoint: str = SOLANA_DEVNET_HTTP_ENDPOINT,
        ws_endpoint: str = SOLANA_DEVNET_WS_ENDPOINT
    ):
        """
        Initialises a new Solana API client.

        Args:
            ratelimit (Union[False, RateLimit, None]): the rate limit; defaults
                to a global rate limit based on the endpoint; specify False to
                disable rate limiting
            client (aiohttp.ClientSession): the aiohttp ClientSession to use,
                will create one on first use otherwise
            endpoint (str): the URL to the HTTP endpoint; defaults to the Solana
                devnet endpoint
            ws_endpoint (str): the URL to the WebSocket endpoint; defaults to
                the Solana devnet endpoint
        """

        # can't create one now as the ClientSession has to be created while in an
        # event loop, which we may not yet be in
        self._client = client
        self._is_own_client = False
        self.endpoint = endpoint
        self.ws_endpoint = ws_endpoint
        self.ratelimit: Union[RateLimit, Literal[False]] = (
            RateLimit.get_endpoint_ratelimit(endpoint)
            if ratelimit is None
            else ratelimit
        )
        self._next_id = 0
        self._ws: Optional[aiohttp.ClientWebSocketResponse] = None
        self._pending_updates: asyncio.Queue[Dict[str, Any]] = asyncio.Queue()

    def _get_next_id(self):
        id = self._next_id
        self._next_id += 1
        return id

    def _get_client(self) -> aiohttp.ClientSession:
        client = self._client
        if client is None:
            client = self._client = aiohttp.ClientSession()
            self._is_own_client = True
        return client

    async def close(self):
        """
        Closes the underlying aiohttp ClientSession, if it was created by this
        SolanaClient.
        """
        if self._is_own_client:
            await self._get_client().close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type: Any, exc_value: Any, traceback: Any):
        await self.close()

    async def update_accounts(self, accounts: Sequence[SolanaAccount]) -> None:
        # Solana's getMultipleAccounts RPC is limited to 100 accounts
        # Hence we have to split them into groups of 100
        # https://docs.solana.com/developing/clients/jsonrpc-api#getmultipleaccounts
        for grouped_accounts in [accounts[i:i+100] for i in range(0, len(accounts), 100)]:
            resp = await self.get_account_info([account.key for account in grouped_accounts])
            slot = resp["context"]["slot"]
            values = resp["value"]
            for account, value in zip(grouped_accounts, values):
                if value is None:
                    logger.warning("got null value from Solana getMultipleAccounts for {}; non-existent account?", account.key)
                    continue
                try:
                    account.update_with_rpc_response(slot, value)
                except Exception as ex:
                    logger.exception("error while updating account {}", account.key, exception=ex)

    async def http_send(self, method: str, params: Optional[List[Any]] = None, *, return_error: bool = False) -> Any:
        if self.ratelimit:
            await self.ratelimit.apply_method(method, True)
        id = self._get_next_id()
        async with self._get_client().post(
            self.endpoint, json=_make_jsonrpc(id, method, params)
        ) as resp:
            if resp.status == 429:  # rate-limited (429 Too Many Requests)
                raise RateLimitedException()
            data = await resp.json()
            if not isinstance(data, dict):
                raise SolanaException(f"got non-JSON-object {type(data)} from Solana")
            data = cast(Dict[str, Any], data)
            received_id: Any = data.get("id")
            if received_id != id:
                raise SolanaException(
                    f"got response with ID {received_id} to request with ID {id}"
                )
            error: Any = data.get("error")
            if error and not return_error:
                raise SolanaException(
                    f"Solana RPC error: {error['code']} {error['message']}", error
                )
            return error or data.get("result")

    async def get_account_info(
        self,
        key: Union[SolanaPublicKeyOrStr, Sequence[SolanaPublicKeyOrStr]],
        commitment: str = SolanaCommitment.CONFIRMED,
        encoding: str = "base64",
    ) -> Dict[str, Any]:
        if isinstance(key, Sequence) and not isinstance(key, str):
            return await self.http_send(
                "getMultipleAccounts",
                [[str(k) for k in key], {"commitment": commitment, "encoding": encoding}],
            )
        else:
            return await self.http_send(
                "getAccountInfo",
                [str(key), {"commitment": commitment, "encoding": encoding}],
            )

    async def get_program_accounts(
        self,
        key: SolanaPublicKeyOrStr,
        commitment: str = SolanaCommitment.CONFIRMED,
        encoding: str = "base64",
        with_context: bool = True
    ) -> Dict[str, Any]:
        return await self.http_send(
            "getProgramAccounts",
            [str(key), {"commitment": commitment, "encoding": encoding, "withContext": with_context}],
        )

    async def get_balance(
        self,
        key: SolanaPublicKeyOrStr,
        commitment: str = SolanaCommitment.CONFIRMED
    ) -> Dict[str, Any]:
        return await self.http_send(
            "getBalance",
            [str(key), {"commitment": commitment}]
        )

    async def get_block_time(
        self,
        slot: int
    ) -> Optional[int]:
        return await self.http_send(
            "getBlockTime",
            [slot]
        )

    async def get_health(self) -> Union[Literal['ok'], Dict[str, Any]]:
        return await self.http_send("getHealth", return_error=True)

    async def get_cluster_nodes(self) -> List[Dict[str, Any]]:
        return await self.http_send("getClusterNodes")

    async def get_slot(
        self,
        commitment: str = SolanaCommitment.CONFIRMED,
        ) -> Union[int, Dict[str, Any]]:
        return await self.http_send(
            "getSlot",
            [{"commitment": commitment}]
        )

    async def ws_account_subscribe(
        self,
        key: SolanaPublicKeyOrStr,
        commitment: str = SolanaCommitment.CONFIRMED,
        encoding: str = "base64",
    ):
        return await self.ws_send(
            "accountSubscribe",
            [str(key), {"commitment": commitment, "encoding": encoding}],
        )

    async def ws_program_subscribe(
        self,
        key: SolanaPublicKeyOrStr,
        commitment: str = SolanaCommitment.CONFIRMED,
        encoding: str = "base64",
    ):
        return await self.ws_send(
            "programSubscribe",
            [str(key), {"commitment": commitment, "encoding": encoding}],
        )

    async def ws_program_unsubscribe(self, subscription_id: int):
        return await self.ws_send(
            "programUnsubscribe",
            [subscription_id],
        )

    async def ws_account_unsubscribe(self, subscription_id: int):
        return await self.ws_send(
            "accountUnsubscribe",
            [subscription_id],
        )

    @property
    def ws_connected(self):
        return self._ws and not self._ws.closed

    @backoff.on_exception(
        backoff.fibo,
        aiohttp.ClientError,
        max_tries=config.get_backoff_max_tries,
        max_value=config.get_backoff_max_value,
    )
    async def ws_connect(self):
        if self.ws_connected:
            return
        self._pending_updates = asyncio.Queue()
        logger.debug("connecting to Solana RPC via WebSocket {}...", self.ws_endpoint)
        self._ws = await self._get_client().ws_connect(self.ws_endpoint)
        logger.debug("connected to Solana RPC via WebSocket")

    async def ws_disconnect(self):
        if not self.ws_connected:
            return
        assert self._ws
        logger.debug("closing Solana RPC WebSocket connection...")
        await self._ws.close()
        logger.debug("closed Solana RPC WebSocket connection")
        self._ws = None

    async def ws_send(self, method: str, params: List[Any]):
        await self.ws_connect()
        if self.ratelimit:
            await self.ratelimit.apply_method(method, True)
        assert self._ws
        id = self._get_next_id()
        await self._ws.send_str(json.dumps(_make_jsonrpc(id, method, params)))
        return await self._ws_wait_response(id)

    async def _ws_wait_response(self, id: int):
        while True:
            msg = json.loads(await self._ws_receive_str())
            if "method" in msg:
                self._pending_updates.put_nowait(msg)
                continue
            received_id = msg.get("id")
            if received_id != id:
                raise SolanaException(
                    f"got response with ID {received_id} to request with ID {id}"
                )
            error = msg.get("error")
            if error:
                raise SolanaException(
                    f"Solana RPC error: {error['code']} {error['message']}", error
                )
            return msg.get("result")

    async def _ws_receive_str(self) -> str:
        # aiohttp's receive_str throws a very cryptic error when the
        # connection is closed while we are waiting
        # handle that ourselves
        assert self._ws
        wsmsg = await self._ws.receive()
        wsmsgtype: aiohttp.WSMsgType = wsmsg.type # type: ignore  # missing type information
        if wsmsgtype == aiohttp.WSMsgType.CLOSED or wsmsgtype == aiohttp.WSMsgType.CLOSING:
            logger.debug("WebSocket closed while waiting for message", wsmsg)
            raise WebSocketClosedException(f"WebSocket closed while waiting for update; close code was {self._ws.close_code}")
        elif wsmsgtype != aiohttp.WSMsgType.TEXT:
            raise SolanaException(f"Unexpected WebSocket message type {wsmsgtype} from Solana")
        return wsmsg.data # type: ignore  # missing type information

    async def get_next_update(self) -> Dict[str, Any]:
        if not self._pending_updates.empty():
            return self._pending_updates.get_nowait()
        msg = json.loads(await self._ws_receive_str())
        if "method" not in msg:
            raise SolanaException(f"unexpected RPC response", msg)
        return msg


def _make_jsonrpc(id: int, method: str, params: Optional[List[Any]]) -> Dict[str, Any]:
    r: Dict[str, Any] = {"jsonrpc": "2.0", "id": id, "method": method}
    if params:
        r["params"] = params
    return r
