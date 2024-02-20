from pythclient.hermes import HermesClient, PriceFeed

BTC_ID = "e62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43"  # BTC/USD
ETH_ID = "ff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace"  # ETH/USD

async def test_hermes_return_price_feed_object():
    # Test that the hermes get request returns a dict with same keys as PriceFeed
    hermes_client = HermesClient([])
    hermes_client.add_feed_ids([BTC_ID, ETH_ID])

    all_prices = await hermes_client.get_all_prices()

    assert isinstance(all_prices, dict)
    assert set(all_prices[BTC_ID].keys()) == set(PriceFeed.__annotations__.keys())
    assert set(all_prices[ETH_ID].keys()) == set(PriceFeed.__annotations__.keys())