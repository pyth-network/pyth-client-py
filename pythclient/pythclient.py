"""Python client for the Pyth oracle on the Solana blockchain."""

from __future__ import annotations
from asyncio.futures import Future
from typing import List, Optional, Union, Any, Dict, Coroutine, Tuple, Iterable
from typing_extensions import Literal
import asyncio

import aiohttp
import backoff
from loguru import logger

from .solana import SolanaAccount, SolanaClient, SolanaPublicKey, SOLANA_DEVNET_HTTP_ENDPOINT, SOLANA_DEVNET_WS_ENDPOINT, SolanaPublicKeyOrStr
from .pythaccounts import PythAccount, PythMappingAccount, PythProductAccount, PythPriceAccount
from . import exceptions, config, ratelimit


class PythClient:
    def __init__(self, *,
                 solana_client: Optional[SolanaClient] = None,
                 solana_endpoint: str = SOLANA_DEVNET_HTTP_ENDPOINT,
                 solana_ws_endpoint: str = SOLANA_DEVNET_WS_ENDPOINT,
                 first_mapping_account_key: str,
                 program_key: Optional[str] = None,
                 aiohttp_client_session: Optional[aiohttp.ClientSession] = None) -> None:
        self._first_mapping_account_key = SolanaPublicKey(first_mapping_account_key)
        self._program_key = program_key and SolanaPublicKey(program_key)
        self.solana = solana_client or SolanaClient(endpoint=solana_endpoint, ws_endpoint=solana_ws_endpoint, client=aiohttp_client_session)
        self._products: Optional[List[PythProductAccount]] = None
        self._mapping_accounts: Optional[List[PythMappingAccount]] = None

    @property
    def solana_ratelimit(self) -> Union[ratelimit.RateLimit, Literal[False]]:
        return self.solana.ratelimit

    @property
    def products(self) -> List[PythProductAccount]:
        if self._products is not None:
            return self._products
        raise exceptions.NotLoadedException()

    async def get_products(self) -> List[PythProductAccount]:
        if self._products is not None:
            return self._products
        return await self.refresh_products()

    def refresh_products(self) -> Coroutine[Any, Any, List[PythProductAccount]]:
        return self._refresh_products()

    @backoff.on_exception(
        backoff.fibo,
        (aiohttp.ClientError, exceptions.RateLimitedException),
        max_tries=config.get_backoff_max_tries,
        max_value=config.get_backoff_max_value,
    )
    async def refresh_all_prices(self) -> None:
        # do we have a program account key?
        if self._program_key:
            # use getProgramAccounts
            slot, account_json = await self._refresh_using_program()
        else:
            slot, account_json = None, None

        products = await self.get_products()
        tuples: List[Tuple[PythProductAccount, List[PythPriceAccount], PythPriceAccount]] = [
            (product, [], PythPriceAccount(product.first_price_account_key, self.solana, product=product))
                for product in products
                if product.first_price_account_key is not None
        ]

        while len(tuples) > 0:
            if account_json is not None:
                assert slot
                for _, _, price in tuples:
                    p_data = account_json.get(str(price.key))
                    if p_data is None:
                        raise exceptions.MissingAccountException(f"need account {price.key} but missing in getProgramAccount response")
                    price.update_with_rpc_response(slot, p_data)
            else:
                await self.solana.update_accounts([price for _, _, price in tuples])

            next_tuples: List[Tuple[PythProductAccount, List[PythPriceAccount], PythPriceAccount]] = []
            for product, prices, price in tuples:
                prices.append(price)
                if price.next_price_account_key:
                    next_tuples.append((product, prices, PythPriceAccount(price.next_price_account_key, self.solana, product=product)))
                else:
                    product.use_price_accounts(prices)
            tuples = next_tuples

    @backoff.on_exception(
        backoff.fibo,
        (aiohttp.ClientError, exceptions.RateLimitedException),
        max_tries=config.get_backoff_max_tries,
        max_value=config.get_backoff_max_value,
    )
    async def _refresh_using_program(self) -> Tuple[int, Dict[str, Any]]:
        # get all prices using getProgramAccounts
        assert self._program_key
        resp = await self.solana.get_program_accounts(self._program_key, with_context=True)
        slot: int = resp['context']['slot']
        account_json: Dict[str, Any] = dict((account['pubkey'], account['account']) for account in resp['value'])

        if self._mapping_accounts is None:
            await self._refresh_mapping_accounts(account_json=account_json, slot=slot)
        if self._products is None:
            await self._refresh_products(account_json=account_json, slot=slot)

        return slot, account_json

    def create_watch_session(self):
        return WatchSession(self.solana)

    async def close(self):
        await self.solana.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type: Any, exc_value: Any, traceback: Any):
        await self.close()

    @backoff.on_exception(
        backoff.fibo,
        (aiohttp.ClientError, exceptions.RateLimitedException),
        max_tries=config.get_backoff_max_tries,
        max_value=config.get_backoff_max_value,
    )
    async def _refresh_products(self, *, update_accounts: bool = True, account_json: Optional[Dict[str, Any]] = None, slot: Optional[int] = None) -> List[PythProductAccount]:
        if update_accounts or not self._mapping_accounts:
            await self._refresh_mapping_accounts()
        assert self._mapping_accounts is not None

        product_account_keys: List[SolanaPublicKey] = []
        for mapping_account in self._mapping_accounts:
            product_account_keys.extend(mapping_account.entries)

        existing_products = dict((product.key, product) for product in self._products) if self._products else {}

        products: List[PythProductAccount] = []
        for k in product_account_keys:
            product = existing_products.get(k) or PythProductAccount(k, self.solana)
            if account_json is not None:
                p_data = account_json.get(str(k))
                if p_data is None:
                    raise exceptions.MissingAccountException(f"need account {k} but missing in getProgramAccount response")
                assert slot
                product.update_with_rpc_response(slot, p_data)
            products.append(product)
        if account_json is None and update_accounts:
            await self.solana.update_accounts(products)
        self._products = products
        return self._products

    async def get_mapping_accounts(self) -> List[PythMappingAccount]:
        if self._mapping_accounts is not None:
            return self._mapping_accounts
        return await self._refresh_mapping_accounts()

    async def get_all_accounts(self) -> List[PythAccount]:
        accounts: List[PythAccount] = []
        accounts.extend(await self.get_mapping_accounts())
        for product in await self.get_products():
            accounts.append(product)
            accounts.extend((await product.get_prices()).values())
        return accounts

    @backoff.on_exception(
        backoff.fibo,
        (aiohttp.ClientError, exceptions.RateLimitedException),
        max_tries=config.get_backoff_max_tries,
        max_value=config.get_backoff_max_value,
    )
    async def _refresh_mapping_accounts(self, *, account_json: Optional[Dict[str, Any]] = None, slot: Optional[int] = None) -> List[PythMappingAccount]:
        key = self._first_mapping_account_key

        existing_mappings = dict((mapping.key, mapping) for mapping in self._mapping_accounts) if self._mapping_accounts else {}

        mapping_accounts: List[PythMappingAccount] = []
        while key:
            m = existing_mappings.get(key) or PythMappingAccount(key, self.solana)
            if account_json is not None:
                m_data = account_json.get(str(key))
                if m_data is None:
                    raise exceptions.MissingAccountException(f"need account {key} but missing in getProgramAccount response")
                assert slot
                m.update_with_rpc_response(slot, m_data)
            else:
                await m.update()
            mapping_accounts.append(m)
            key = m.next_account_key
        self._mapping_accounts = mapping_accounts
        return self._mapping_accounts

    async def check_mapping_changes(self) -> Tuple[List[Union[PythMappingAccount, PythProductAccount]], List[Union[PythMappingAccount, PythProductAccount]]]:
        assert self._mapping_accounts
        assert self._products
        # collect old keys
        old_accounts = dict((product.key, product) for product in [*self._mapping_accounts, *self._products])

        await self._refresh_mapping_accounts()

        # re-collect product accounts
        await self._refresh_products(update_accounts=False)

        new_accounts = dict((product.key, product) for product in [*self._mapping_accounts, *self._products])
        added_keys = new_accounts.keys() - old_accounts.keys()
        removed_keys = old_accounts.keys() - new_accounts.keys()
        for new_key in added_keys:
            await new_accounts[new_key].update()

        return list(new_accounts[key] for key in added_keys), list(old_accounts[key] for key in removed_keys)


def _WatchSession_reconnect_giveup(e: BaseException):
    return isinstance(e, asyncio.CancelledError)


class WatchSession:
    def __init__(self, client: SolanaClient):
        self._client = client
        self._connected = False

        self._pending_sub: Dict[str, SolanaAccount] = {}
        self._subid_to_account: Dict[int, SolanaAccount] = {}
        self._accountkey_to_subid: Dict[str, int] = {}

        self._pending_program_sub: Dict[str, Dict[str, SolanaAccount]] = {}
        self._subid_to_program_accounts: Dict[int, Dict[str, SolanaAccount]] = {}
        self._programkey_to_subid: Dict[str, int] = {}
        self._request_id = 1
        self._reconnect_future: Optional[Future[Any]] = None

    def _next_subid(self) -> int:
        id = self._request_id
        self._request_id += 1
        return id

    @backoff.on_exception(backoff.fibo,
        Exception,
        max_tries=config.get_backoff_max_tries,
        max_value=config.get_backoff_max_value,
        giveup=_WatchSession_reconnect_giveup)
    async def reconnect(self):
        if self._reconnect_future:
            await self._reconnect_future
            return
        try:
            self._reconnect_future = asyncio.get_event_loop().create_future()
            logger.debug("reconnecting WebSocket...")
            await self.disconnect()
            await self.connect()

            resubscribe_accounts: List[SolanaAccount] = []
            resubscribe_accounts.extend(self._pending_sub.values())
            resubscribe_accounts.extend(self._subid_to_account.values())
            logger.debug("connected, resubscribing to {} accounts...", len(resubscribe_accounts))
            self._pending_sub = {}
            self._subid_to_account = {}
            self._accountkey_to_subid = {}
            for account in resubscribe_accounts:
                await self._subscribe(account, True)
            logger.debug("resubscribed")

            resubscribe_programs: List[Tuple[str, Dict[str, SolanaAccount]]] = []
            resubscribe_programs.extend(self._pending_program_sub.items())
            resubscribe_programs.extend((key, self._subid_to_program_accounts[subid]) for key, subid in self._programkey_to_subid.items())
            logger.debug("connected, resubscribing to {} program accounts...", len(resubscribe_programs))
            self._pending_program_sub = {}
            self._programkey_to_subid = {}
            self._subid_to_program_accounts = {}
            for key, accounts in resubscribe_programs:
                await self._program_subscribe(key, accounts.values(), True)
            logger.debug("resubscribed")
        finally:
            if self._reconnect_future:
                future, self._reconnect_future = self._reconnect_future, None
                future.set_result(None)

    async def connect(self):
        await self._client.ws_connect()

    async def disconnect(self):
        try:
            await self._client.ws_disconnect()
        except Exception as e:
            if isinstance(e, asyncio.CancelledError):
                raise
            logger.exception("exception while disconnecting WebSocket", exception=e)
            pass

    async def _subscribe(self, account: SolanaAccount, reconnecting: bool = False):
        try:
            keystr = str(account.key)
            if keystr in self._accountkey_to_subid:
                return
            logger.trace("subscribing to {}...", keystr)
            self._pending_sub[keystr] = account
            subid = await self._client.ws_account_subscribe(keystr)
            logger.trace("subscribed to {} with subid {}", keystr, subid)
            del self._pending_sub[keystr]
            self._accountkey_to_subid[keystr] = subid
            self._subid_to_account[subid] = account
        except Exception as e:
            if isinstance(e, asyncio.CancelledError):
                raise
            logger.exception("exception while subscribing to account", exception=e)
            if not reconnecting:
                await self.reconnect()

    def subscribe(self, account: SolanaAccount):
        return self._subscribe(account)

    async def unsubscribe(self, account: SolanaAccount):
        keystr = str(account.key)
        subid = self._accountkey_to_subid.pop(keystr, None)
        if subid is None:
            return
        del self._subid_to_account[subid]
        try:
            logger.trace("unsubscribing from {} with subid {}...", keystr, subid)
            await self._client.ws_account_unsubscribe(subid)
            logger.trace("unsubscribed from {}", keystr)
        except Exception as e:
            if isinstance(e, asyncio.CancelledError):
                raise
            logger.exception("exception while unsubscribing from account", exception=e)
            await self.reconnect()

    async def _program_subscribe(self, programkey: SolanaPublicKeyOrStr, accounts: Iterable[SolanaAccount], reconnecting: bool = False):
        try:
            keystr = str(programkey)
            if keystr in self._programkey_to_subid:
                return
            logger.trace("subscribing to program {} accounts...", keystr)

            accounts_dict = dict((str(account.key), account) for account in accounts)
            self._pending_program_sub[keystr] = accounts_dict
            subid = await self._client.ws_program_subscribe(keystr)
            logger.trace("subscribed to program {} with subid {}", keystr, subid)
            del self._pending_program_sub[keystr]
            self._programkey_to_subid[keystr] = subid
            self._subid_to_program_accounts[subid] = accounts_dict
        except Exception as e:
            if isinstance(e, asyncio.CancelledError):
                raise
            logger.exception("exception while subscribing to program", exception=e)
            if not reconnecting:
                await self.reconnect()

    def program_subscribe(self, programkey: SolanaPublicKeyOrStr, accounts: Iterable[SolanaAccount]):
        return self._program_subscribe(programkey, accounts)

    async def program_unsubscribe(self, programkey: SolanaPublicKeyOrStr):
        keystr = str(programkey)
        subid = self._programkey_to_subid.pop(keystr, None)
        if subid is None:
            return
        del self._subid_to_program_accounts[subid]
        try:
            logger.trace("unsubscribing from program {} with subid {}...", keystr, subid)
            await self._client.ws_program_unsubscribe(subid)
            logger.trace("unsubscribed from {}", keystr)
        except Exception as e:
            if isinstance(e, asyncio.CancelledError):
                raise
            logger.exception("exception while unsubscribing from program", exception=e)
            await self.reconnect()

    def update_program_accounts(self, programkey: SolanaPublicKeyOrStr, accounts: Iterable[SolanaAccount]):
        keystr = str(programkey)
        if keystr not in self._programkey_to_subid:
            raise ValueError(f"not subscribed to {keystr}")
        accounts_dict = dict((str(account.key), account) for account in accounts)
        self._subid_to_program_accounts[self._programkey_to_subid[keystr]] = accounts_dict

    async def next_update(self) -> SolanaAccount:
        while True:
            try:
                msg = await self._client.get_next_update()
            except asyncio.CancelledError:
                raise
            except exceptions.WebSocketClosedException as e:
                logger.warning(e.args[0])
                await self.reconnect()
                continue
            except Exception as e:
                logger.exception("exception while retrieving update", exception=e)
                await self.reconnect()
                continue

            method = msg.get("method")
            if method == "accountNotification":
                subid = msg["params"]["subscription"]
                slot = msg["params"]["result"]["context"]["slot"]
                account_json = msg["params"]["result"]["value"]
                account = self._subid_to_account[subid]
                account.update_with_rpc_response(slot, account_json)
                return account
            elif method == "programNotification":
                subid = msg["params"]["subscription"]
                slot = msg["params"]["result"]["context"]["slot"]
                account_key = msg["params"]["result"]["value"]["pubkey"]
                account_json = msg["params"]["result"]["value"]["account"]
                account = self._subid_to_program_accounts[subid].get(account_key)
                if account:
                    account.update_with_rpc_response(slot, account_json)
                    return account
                else:
                    logger.warning("got update for account {} from programSubscribe, but this account was never initialised", account_key)
            else:
                logger.debug("unknown method {} update from Solana: {}", method, msg)
