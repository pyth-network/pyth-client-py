from __future__ import annotations
from typing import Union, Optional, Dict
from typing_extensions import Literal
import asyncio
import datetime
from urllib import parse as urlparse

from loguru import logger

RateLimitCPS = Union[float, Literal[False], None]
RateLimitInterval = RateLimitCPS

def _compute_sleep(now: datetime.datetime, interval: float, last_use: Optional[datetime.datetime] = None) -> float:
    if last_use is None or interval is None:
        return 0
    since_last_use = (now - last_use).total_seconds()
    if since_last_use >= interval:
        return 0
    return min(interval - since_last_use, interval)


def _calculate_interval(cps_argument: RateLimitCPS) -> RateLimitInterval:
    if cps_argument is False or cps_argument is None:
        return cps_argument
    if cps_argument == 0:
        return None
    return 1 / cps_argument


class RateLimit:
    _endpoint_ratelimit: Dict[str, RateLimit] = {}

    def __init__(self, *,
        overall_cps: RateLimitCPS = False,
        method_cps: RateLimitCPS = False,
        connection_cps: RateLimitCPS = False) -> None:
        """
        Creates a new rate limit.

        Arguments are passed to configure; see configure for details.
        """
        self._overall_interval: RateLimitInterval
        self._method_interval: RateLimitInterval
        self._connection_interval: RateLimitInterval
        self._method_last_invocation: Dict[str, datetime.datetime] = {}
        self._overall_last_invocation: Optional[datetime.datetime] = None
        self._last_connection: Optional[datetime.datetime] = None

        self.configure(overall_cps=overall_cps, method_cps=method_cps, connection_cps=connection_cps)

    def configure(
        self,
        *,
        overall_cps: RateLimitCPS = False,
        method_cps: RateLimitCPS = False,
        connection_cps: RateLimitCPS = False,
    ) -> None:
        """
        Configure the rate limits.

        If an argument is specified as None or 0, then it is taken as no rate limit.

        If an argument is specified as False, then the rate limit is taken from
        the global default.

        Args:
            overall_cps: overall calls per second (applied across all methods)
            method_cps: per-method calls per second
            connection_cps: connections per second
        """
        self._overall_interval = _calculate_interval(overall_cps)
        self._method_interval = _calculate_interval(method_cps)
        self._connection_interval = _calculate_interval(connection_cps)


    @staticmethod
    def _return_interval(instance_interval: RateLimitInterval, default_interval: RateLimitInterval) -> float:
        if instance_interval is None or instance_interval == 0:
            return 0
        elif instance_interval is False:
            return default_interval or 0
        return instance_interval

    def _get_overall_interval(self) -> float:
        return RateLimit._return_interval(self._overall_interval, _default_ratelimit._overall_interval)

    def _get_method_interval(self) -> float:
        return RateLimit._return_interval(self._method_interval, _default_ratelimit._method_interval)

    def _get_connection_interval(self) -> float:
        return RateLimit._return_interval(self._connection_interval, _default_ratelimit._connection_interval)

    async def apply_method(self, method: str, connection: bool = False) -> None:
        now = datetime.datetime.now()
        sleep_for = max(
            _compute_sleep(
                now, self._get_overall_interval(), self._overall_last_invocation
            ),
            _compute_sleep(
                now,
                self._get_method_interval(),
                self._method_last_invocation.get(method),
            ),
        )
        if connection:
            sleep_for = max(
                sleep_for,
                _compute_sleep(
                    now, self._get_connection_interval(), self._last_connection
                ),
            )
        invoke_at = now + datetime.timedelta(seconds=sleep_for)
        self._method_last_invocation[method] = self._overall_last_invocation = invoke_at
        if connection:
            self._last_connection = invoke_at
        if sleep_for == 0:
            return
        logger.trace("sleeping {} s before method {}", sleep_for, method)
        await asyncio.sleep(sleep_for)

    async def apply_connection(self):
        now = datetime.datetime.now()
        sleep_for = _compute_sleep(
            now, self._get_connection_interval(), self._last_connection
        )
        self._last_connection = now + datetime.timedelta(seconds=sleep_for)
        if sleep_for == 0:
            return
        logger.trace("sleeping {} s before connecting", sleep_for)
        await asyncio.sleep(sleep_for)

    @classmethod
    def get_endpoint_ratelimit(cls, endpoint: str) -> RateLimit:
        """
        Returns the RateLimit object for a given host, given the endpoint URL.

        The RateLimit is shared per-host i.e. https://api.devnet.solana.com and
        wss://api.devnet.solana.com share a RateLimit.
        """
        host = urlparse.urlsplit(endpoint)[1]
        if ':' in host:
            host = host.split(':')[0]
        ratelimit = cls._endpoint_ratelimit.get(host)
        if ratelimit is None:
            ratelimit = RateLimit()
            cls._endpoint_ratelimit[host] = ratelimit
        return ratelimit

    @classmethod
    def configure_endpoint_ratelimit(cls, endpoint: str, *,
                                     overall_cps: RateLimitCPS = False,
                                     method_cps: RateLimitCPS = False,
                                     connection_cps: RateLimitCPS = False):
        ratelimit = cls.get_endpoint_ratelimit(endpoint)
        ratelimit.configure(overall_cps=overall_cps, method_cps=method_cps, connection_cps=connection_cps)

    @staticmethod
    def configure_default_ratelimit(overall_cps: RateLimitCPS = False,
                                    method_cps: RateLimitCPS = False,
                                    connection_cps: RateLimitCPS = False):
        _default_ratelimit.configure(overall_cps=overall_cps, method_cps=method_cps, connection_cps=connection_cps)


_default_ratelimit = RateLimit(
    overall_cps=None, method_cps=None, connection_cps=None
)
