from __future__ import annotations
from typing import List, Dict, Tuple, Optional, Any, ClassVar
import base64
from enum import Enum
from dataclasses import dataclass, field
import struct

from loguru import logger

from pythclient.market_schedule import MarketSchedule

from . import exceptions
from .solana import SolanaPublicKey, SolanaPublicKeyOrStr, SolanaClient, SolanaAccount


_MAGIC = 0xA1B2C3D4
_VERSION_1 = 1
_VERSION_2 = 2
_SUPPORTED_VERSIONS = set((_VERSION_1, _VERSION_2))
ACCOUNT_HEADER_BYTES = 16  # magic + version + type + size, u32 * 4
_NULL_KEY_BYTES = b'\x00' * SolanaPublicKey.LENGTH
DEFAULT_MAX_LATENCY = 25


class PythAccountType(Enum):
    UNKNOWN = 0
    MAPPING = 1
    PRODUCT = 2
    PRICE = 3


class PythPriceStatus(Enum):
    UNKNOWN = 0
    TRADING = 1
    HALTED = 2
    AUCTION = 3
    IGNORED = 4


class PythPriceType(Enum):
    UNKNOWN = 0
    PRICE = 1


# Join exponential moving average for EMA price and EMA confidence
class EmaType(Enum):
    UNKNOWN = 0
    EMA_PRICE_VALUE = 1
    EMA_PRICE_NUMERATOR = 2
    EMA_PRICE_DENOMINATOR = 3
    EMA_CONFIDENCE_VALUE = 4
    EMA_CONFIDENCE_NUMERATOR = 5
    EMA_CONFIDENCE_DENOMINATOR = 6


def _check_base64(format: str):
    # Solana should return base64 by default, but add a sanity check..
    if format != "base64":
        raise Exception(f"unexpected data type from Solana: {format}")


def _read_public_key_or_none(buffer: bytes, offset: int = 0) -> Optional[SolanaPublicKey]:
    buffer = buffer[offset:offset + SolanaPublicKey.LENGTH]
    if buffer == _NULL_KEY_BYTES:
        return None
    return SolanaPublicKey(buffer)


def _read_attribute_string(buffer: bytes, offset: int) -> Tuple[Optional[str], int]:
    # attribute string format:
    # length (u8)
    # chars (char[length])

    length = buffer[offset]
    if length == 0:
        return None, offset
    data_end = offset + 1 + length
    data = buffer[offset + 1:data_end]

    return data.decode('utf8', 'replace'), data_end


def _parse_header(buffer: bytes, offset: int = 0, *, key: SolanaPublicKeyOrStr) -> Tuple[PythAccountType, int, int]:
    if len(buffer) - offset < ACCOUNT_HEADER_BYTES:
        raise ValueError("Pyth account data too short")

    # Pyth magic (u32) == MAGIC
    # version (u32) == VERSION_1 or 2
    # account type (u32)
    # account data size (u32)
    magic, version, type_, size = struct.unpack_from("<IIII", buffer, offset)

    if len(buffer) < size:
        raise ValueError(
            f"{key} Pyth header says data is {size} bytes, but buffer only has {len(buffer)} bytes")

    if magic != _MAGIC:
        raise ValueError(
            f"{key} Pyth account data header has wrong magic: expected {_MAGIC:08x}, got {magic:08x}")

    if version not in _SUPPORTED_VERSIONS:
        raise ValueError(
            f"{key} Pyth account data has unsupported version {version}")

    return PythAccountType(type_), size, version


class PythAccount(SolanaAccount):
    """
    Represents a Pyth account.
    """

    def __init__(self, key: SolanaPublicKeyOrStr, solana: SolanaClient) -> None:
        super().__init__(key, solana)

    def update_from(self, buffer: bytes, *, version: int, offset: int = 0) -> None:
        """
        Update the data in this object from the Pyth account data in buffer at
        the given offset.

        This method must be overridden in subclasses.
        """
        raise NotImplementedError("update_from should be overridden")

    def update_with_rpc_response(self, slot: int, value: Dict[str, Any]) -> None:
        """
        Update the data in this object from the given JSON RPC response from the
        Solana node.
        """
        super().update_with_rpc_response(slot, value)
        if "data" not in value:
            logger.error("invalid account data response from Solana for key {}: {}", self.key, value)
            raise ValueError(f"invalid account data response from Solana for key {self.key}: {value}")
        data_base64, data_format = value["data"]
        _check_base64(data_format)
        data = base64.b64decode(data_base64)
        type_, size, version = _parse_header(data, 0, key=self.key)
        class_ = _ACCOUNT_TYPE_TO_CLASS.get(type_, None)
        if class_ is not type(self):
            raise ValueError(
                f"wrong Pyth account type {type_} for {type(self)}")

        try:
            self.update_from(data[:size], version=version, offset=ACCOUNT_HEADER_BYTES)
        except Exception as e:
            logger.exception("error while parsing account", exception=e)


class PythMappingAccount(PythAccount):
    """
    Represents a mapping account, which simply contains a list of product
    accounts and a pointer (the public key) to the next mapping account.

    Attributes:
        entries (List[SolanaPublicKey]): a list of public keys of product
            accounts
        next_account_key (Optional[SolanaPublicKey]): the public key of the
            next mapping account, if any
    """

    def __init__(self, key: SolanaPublicKeyOrStr, solana: SolanaClient) -> None:
        super().__init__(key, solana)
        self.entries: List[SolanaPublicKey] = []
        self.next_account_key: Optional[SolanaPublicKey] = None

    def update_from(self, buffer: bytes, *, version: int, offset: int = 0) -> None:
        """
        Update the data in this Mapping account from the given buffer.

        Structure:
            number of products (u32)
            unused (u32)
            next mapping account key (char[32])
        """
        fmt = "<II32s"  # 32 == SolanaPublicKey.LENGTH

        num_entries, _, next_account_key_bytes = struct.unpack_from(
            fmt, buffer, offset)
        next_account_key = _read_public_key_or_none(next_account_key_bytes)

        # product account keys (char[32] * number of products)
        offset += struct.calcsize(fmt)
        entries: List[SolanaPublicKey] = []
        for _ in range(num_entries):
            new_key = SolanaPublicKey(buffer[offset:offset + SolanaPublicKey.LENGTH])
            # ignore null keys..
            if new_key != SolanaPublicKey.NULL_KEY:
                entries.append(SolanaPublicKey(buffer[offset:offset + SolanaPublicKey.LENGTH]))
            else:
                logger.warning("null key seen in mapping account {}", self.key)
            offset += SolanaPublicKey.LENGTH

        self.entries: List[SolanaPublicKey] = entries
        self.next_account_key = next_account_key

    def __str__(self) -> str:
        return f"PythMappingAccount ({self.key})"


class PythProductAccount(PythAccount):
    """
    Represents a product account, which contains metadata about the product
    (asset type, symbol, etc.) and a pointer (the public key) to the first price
    account.

    Attributes:
        first_price_account_key (SolanaPublicKey): the public key of the first price account (the price accounts form a linked list)
        attrs (dict): a dictionary of metadata attributes
    """
    def __init__(self, key: SolanaPublicKey, solana: SolanaClient) -> None:
        super().__init__(key, solana)
        self._prices: Optional[Dict[PythPriceType, PythPriceAccount]] = None
        self.attrs: Dict[str, str] = {}
        self.first_price_account_key: Optional[SolanaPublicKey] = None

    @property
    def prices(self) -> Dict[PythPriceType, PythPriceAccount]:
        """
        Gets the price accounts of this product.

        Raises NotLoadedException if they are not yet loaded.
        """

        if self._prices is not None:
            return self._prices
        raise exceptions.NotLoadedException()

    @property
    def symbol(self) -> str:
        """
        Gets this account's symbol, or 'Unknown' if there is no 'symbol' attribute.
        """
        return self.attrs.get("symbol", "Unknown")
    
    @property
    def schedule(self) -> MarketSchedule:
        """
        Gets the market schedule for this product. If the schedule is not set, returns an always open schedule.
        """
        return MarketSchedule(self.attrs.get("schedule", "America/New_York;O,O,O,O,O,O,O;"))

    async def get_prices(self) -> Dict[PythPriceType, PythPriceAccount]:
        """
        Gets the price accounts of this product.

        If they are not yet loaded, loads them.
        """

        if self._prices is not None:
            return self._prices
        return await self.refresh_prices()

    async def refresh_prices(self) -> Dict[PythPriceType, PythPriceAccount]:
        """
        Refreshes the price accounts of this product.
        """

        prices: Dict[PythPriceType, PythPriceAccount] = {}
        key = self.first_price_account_key
        while key:
            price: PythPriceAccount = PythPriceAccount(key, self.solana, product=self)
            await price.update()
            prices[price.price_type] = price
            key = price.next_price_account_key
        self._prices = prices
        return prices

    async def check_price_changes(
        self,
        update_accounts: bool = True
    ) -> Tuple[List[PythPriceAccount], List[PythPriceAccount]]:
        """
        Checks for changes to the list of price accounts of this product.

        Returns a tuple of a list of added accounts, and a list of removed accounts.
        """

        if self._prices is None:
            prices = await self.refresh_prices()
            return list(prices.values()), []
        old_prices = dict((price.key, price) for price in self._prices.values())
        new_prices: Dict[PythPriceType, PythPriceAccount] = {}
        added_prices: List[PythPriceAccount] = []
        if update_accounts:
            await self.solana.update_accounts([self, *old_prices.values()])
        key = self.first_price_account_key
        while key:
            account = old_prices.pop(key, None)
            if account is None:
                account = PythPriceAccount(key, self.solana, product=self)
                await account.update()
                added_prices.append(account)
            new_prices[account.price_type] = account
            key = account.next_price_account_key

        self._prices = new_prices
        return added_prices, list(old_prices.values())

    def use_price_accounts(self, new_prices: List[PythPriceAccount]) -> None:
        """
        Use the price accounts provided in the list.

        The first price account must match the first_price_account_key of this product account, and the subsequent price
        accounts must match the next_price_account_key of the preceding price accounts.
        """
        prices: Dict[PythPriceType, PythPriceAccount] = {}
        expected_key = self.first_price_account_key
        for price in new_prices:
            if price.key != expected_key:
                logger.error("expected price account {}, got {}", expected_key, price.key)
                raise ValueError(f"expected price account {expected_key}, got {price.key}")
            prices[price.price_type] = price
            expected_key = price.next_price_account_key
        if expected_key is not None:
            logger.error("expected price account {} but end of list reached", expected_key)
            raise ValueError("missing price account")
        self._prices = prices

    def update_from(self, buffer: bytes, *, version: int, offset: int = 0) -> None:
        """
        Update the data in this product account from the given buffer.

        Structure:
            first price account key (char[32])
            attributes
            {
              key (attribute string)
              value (attribute string)
            }
            repeat until end of data or key is empty
        """

        first_price_account_key_bytes = buffer[offset:offset +
                                               SolanaPublicKey.LENGTH]
        attrs = {}

        offset += SolanaPublicKey.LENGTH
        buffer_len = len(buffer)
        while offset < buffer_len:
            key, offset = _read_attribute_string(buffer, offset)
            if key is None:
                break
            value, offset = _read_attribute_string(buffer, offset)
            attrs[key] = value

        self.first_price_account_key = SolanaPublicKey(first_price_account_key_bytes)
        if self.first_price_account_key == SolanaPublicKey.NULL_KEY:
            self.first_price_account_key = None
            self._prices = {}
        self.attrs: Dict[str, str] = attrs

    def __str__(self) -> str:
        return f"PythProductAccount {self.symbol} ({self.key})"

    def __repr__(self) -> str:
        return str(self)

    def __iter__(self):
        for key, val in self.__dict__.items():
            if not key.startswith('_'):
                yield key, val


@dataclass
class PythPriceInfo:
    """
    Contains price information.

    Attributes:
        raw_price (int): the raw price
        raw_confidence_interval (int): the raw confidence interval
        price (int): the price
        confidence_interval (int): the price confidence interval
        price_status (PythPriceStatus): the price status
        pub_slot (int): the slot time this price information was published
        exponent (int): the power-of-10 order of the price
    """

    LENGTH: ClassVar[int] = 32

    raw_price: int
    raw_confidence_interval: int
    price_status: PythPriceStatus
    pub_slot: int
    exponent: int

    price: float = field(init=False)
    confidence_interval: float = field(init=False)

    def __post_init__(self):
        self.price = self.raw_price * (10 ** self.exponent)
        self.confidence_interval = self.raw_confidence_interval * \
            (10 ** self.exponent)

    @staticmethod
    def deserialise(buffer: bytes, offset: int = 0, *, exponent: int) -> PythPriceInfo:
        """
        Deserialise the data in the given buffer into a PythPriceInfo object.

        Structure:
            price (i64)
            confidence interval of price (u64)
            status (u32 PythPriceStatus)
            corporate action (u32, currently unused)
            slot (u64)
        """
        # _ is corporate_action
        price, confidence_interval, price_status, _, pub_slot = struct.unpack_from(
            "<qQIIQ", buffer, offset)
        return PythPriceInfo(price, confidence_interval, PythPriceStatus(price_status), pub_slot, exponent)

    def __str__(self) -> str:
        return f"PythPriceInfo status {self.price_status} price {self.price}"

    def __repr__(self) -> str:
        return str(self)


@dataclass
class PythPriceComponent:
    """
    Represents a price component. This is the individual prices each
    publisher sends in addition to their aggregate.

    Attributes:
        publisher_key (SolanaPublicKey): the public key of the publisher
        last_aggregate_price_info (PythPriceInfo): the price information from this
            publisher used in the last aggregate price
        latest_price_info (PythPriceInfo): the latest price information from this
            publisher
        exponent (int): the power-of-10 order for all the raw price information
            in this price component
    """

    LENGTH: ClassVar[int] = SolanaPublicKey.LENGTH + 2 * PythPriceInfo.LENGTH

    publisher_key: SolanaPublicKey
    last_aggregate_price_info: PythPriceInfo
    latest_price_info: PythPriceInfo
    exponent: int

    @staticmethod
    def deserialise(buffer: bytes, offset: int = 0, *, exponent: int) -> Optional[PythPriceComponent]:
        """
        Deserialise the data in the given buffer into a PythPriceComponent object.

        Structure:
            key of quoter (char[32])
            contributing price to last aggregate (PythPriceInfo)
            latest contributing price (PythPriceInfo)
        """
        key = _read_public_key_or_none(buffer, offset)
        if key is None:
            return None
        offset += SolanaPublicKey.LENGTH
        last_aggregate_price = PythPriceInfo.deserialise(
            buffer, offset, exponent=exponent)
        offset += PythPriceInfo.LENGTH
        latest_price = PythPriceInfo.deserialise(buffer, offset, exponent=exponent)
        return PythPriceComponent(key, last_aggregate_price, latest_price, exponent)


class PythPriceAccount(PythAccount):
    """
    Represents a price account, which contains price data of a particular type
    (price_type) for a product.

    Attributes:
        price_type (PythPriceType): the price type
        exponent (int): the power-of-10 order for all the raw price information
            in this price account
        last_slot (int): slot of last valid aggregate price
            information
        valid_slot (int): the slot of the current aggregate price
        product_account_key (SolanaPublicKey): the public key of the product account
        next_price_account_key (Optional[SolanaPublicKey]): the public key of the
            next price account in this product
        aggregator_key (SolanaPublicKey): the public key of the quoter who computed
            the last aggregate price
        aggregate_price_info (PythPriceInfo): the aggregate price information
        price_components (List[PythPriceComponent]): the price components that the
            aggregate price is composed of
        slot (int): the slot time when this account was last fetched
        product (Optional[PythProductAccount]): the product this price is for, if loaded
        max_latency (int): the maximum allowed slot difference for this feed
    """

    def __init__(self, key: SolanaPublicKey, solana: SolanaClient, *, product: Optional[PythProductAccount] = None) -> None:
        super().__init__(key, solana)
        self.product = product
        self.price_type = PythPriceType.UNKNOWN
        self.exponent: Optional[int] = None
        self.num_components: int = 0
        self.last_slot: int = 0
        self.valid_slot: int = 0
        self.product_account_key: Optional[SolanaPublicKey] = None
        self.next_price_account_key: Optional[SolanaPublicKey] = None
        self.aggregate_price_info: Optional[PythPriceInfo] = None
        self.price_components: List[PythPriceComponent] = []
        self.derivations: Dict[EmaType, int] = {}
        self.timestamp: int = 0  # unix timestamp in seconds
        self.min_publishers: Optional[int] = None
        self.prev_slot: int = 0
        self.prev_price: float = field(init=False)
        self.prev_conf: float = field(init=False)
        self.prev_timestamp: int = 0  # unix timestamp in seconds
        self.max_latency: int = 0 # maximum allowed slot difference for this feed

    @property
    def aggregate_price(self) -> Optional[float]:
        """
        The aggregate price. Returns None if price is not currently available.
        If you need the price value regardless of availability use `aggregate_price_info.price`
        """
        if self.aggregate_price_status == PythPriceStatus.TRADING:
            return self.aggregate_price_info.price
        else:
            return None

    @property
    def aggregate_price_confidence_interval(self) -> Optional[float]:
        """
        The aggregate price confidence interval. Returns None if price is not currently available.
        If you need the confidence value regardless of availability use `aggregate_price_info.confidence_interval`
        """
        if self.aggregate_price_status == PythPriceStatus.TRADING:
            return self.aggregate_price_info.confidence_interval
        else:
            return None
   
    @property
    def aggregate_price_status(self) -> Optional[PythPriceStatus]:
        """The aggregate price status."""
        return self.get_aggregate_price_status_with_slot(self.slot)

    def get_aggregate_price_status_with_slot(self, slot: int) -> Optional[PythPriceStatus]:
        """
        Gets the aggregate price status given a solana slot.
        You might consider using this function with the latest solana slot to make sure the price has not gone stale.
        """
        if self.aggregate_price_info.price_status == PythPriceStatus.TRADING and \
            slot - self.aggregate_price_info.pub_slot > self.max_latency:
            return PythPriceStatus.UNKNOWN

        return self.aggregate_price_info.price_status

    def update_from(self, buffer: bytes, *, version: int, offset: int = 0) -> None:
        """
        Update the data in this price account from the given buffer.

        Structure:
            price type (u32 PythPriceType)
            exponent (i32)
            number of component prices (u32)
                (? unclear if this is supposed to match the number of
                    PythPriceComponents below)
            unused (u32)
            currently accumulating price slot (u64)
            slot of current aggregate price (u64)
            derivations (u64[6] - array index corresponds to (DeriveType - 1) - v2 only)
            unused derivation values and minimum publishers (u64[2], i32[2], )
            product account key (char[32])
            next price account key (char[32])
            account key of quoter who computed last aggregate price (char[32])
            aggregate price info (PythPriceInfo)
            price components (PythPriceComponent[up to 16 (v1) / up to 32 (v2)])
        """
        if version == _VERSION_2:
            price_type, exponent, num_components = struct.unpack_from("<IiI", buffer, offset)
            offset += 16  # struct.calcsize("IiII") (last I is the number of quoters that make up the aggregate)
            last_slot, valid_slot = struct.unpack_from("<QQ", buffer, offset)
            offset += 16  # struct.calcsize("QQ")
            derivations = list(struct.unpack_from("<6q", buffer, offset))
            self.derivations = dict((type_, derivations[type_.value - 1]) for type_ in [EmaType.EMA_CONFIDENCE_VALUE, EmaType.EMA_PRICE_VALUE])
            offset += 48  # struct.calcsize("6q")
            timestamp, min_publishers = struct.unpack_from("<qB", buffer, offset)
            offset += 9  # struct.calcsize("qB")
            _message_sent, max_latency = struct.unpack_from("<bB", buffer, offset)
            offset += 2  # struct.calcsize("bB")
            _drv_3, _drv_4 = struct.unpack_from("<bi", buffer, offset)
            offset += 5  # struct.calcsize("bi")
            product_account_key_bytes, next_price_account_key_bytes = struct.unpack_from("32s32s", buffer, offset)
            offset += 64  # struct.calcsize("32s32s")
            prev_slot, prev_price, prev_conf, prev_timestamp = struct.unpack_from("<QqQq", buffer, offset)
            offset += 32  # struct.calcsize("QqQq")
            prev_price *= (10 ** exponent)
            prev_conf *= (10 ** exponent)
        elif version == _VERSION_1:
            price_type, exponent, num_components, _, last_slot, valid_slot, product_account_key_bytes, next_price_account_key_bytes, aggregator_key_bytes = struct.unpack_from(
                "<IiIIQQ32s32s32s", buffer, offset)
            self.derivations = {}
            offset += 128  # struct.calcsize("<IiIIQQ32s32s32s")
        else:
            assert False

        # aggregate price info (PythPriceInfo)
        aggregate_price_info = PythPriceInfo.deserialise(
            buffer, offset, exponent=exponent)

        # price components (PythPriceComponent[up to 16 (v1) / up to 32 (v2)])
        price_components: List[PythPriceComponent] = []
        offset += PythPriceInfo.LENGTH
        buffer_len = len(buffer)
        while offset < buffer_len:
            component = PythPriceComponent.deserialise(
                buffer, offset, exponent=exponent)
            if not component:
                break
            price_components.append(component)
            offset += PythPriceComponent.LENGTH

        self.price_type = PythPriceType(price_type)
        self.exponent = exponent
        self.num_components = num_components
        self.last_slot = last_slot
        self.valid_slot = valid_slot
        self.product_account_key = SolanaPublicKey(product_account_key_bytes)
        self.next_price_account_key = _read_public_key_or_none(
            next_price_account_key_bytes)
        self.aggregate_price_info = aggregate_price_info
        self.price_components = price_components
        self.timestamp = timestamp
        self.min_publishers = min_publishers
        self.prev_slot = prev_slot
        self.prev_price = prev_price
        self.prev_conf = prev_conf
        self.prev_timestamp = prev_timestamp
        # a max latency of 0 is the default max latency
        self.max_latency = max_latency if max_latency != 0 else DEFAULT_MAX_LATENCY

    def __str__(self) -> str:
        if self.product:
            return f"PythPriceAccount {self.product.symbol} {self.price_type} ({self.key})"
        else:
            return f"PythPriceAccount {self.price_type} ({self.key})"


_ACCOUNT_TYPE_TO_CLASS = {
    PythAccountType.MAPPING: PythMappingAccount,
    PythAccountType.PRODUCT: PythProductAccount,
    PythAccountType.PRICE: PythPriceAccount
}
