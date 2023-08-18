from pythclient.price_feeds import encode_vaa_for_chain, vaa_to_price_info

ID = "e62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43"  # BTC/USD
HEX_VAA = "01000000030d00ca037dde1419ea373de7474bff80268e41f55e84dd8e4fa5e5167808111e63e4064efcfd93075d9d162090bc478a017603ef56c4d26e0c46e0af6128c08984470002e9abd7c4e62bbc6b453c5ca014b7313bbadb17d6443190d6679b7c0ccb03bae619d21dcb5d6d5a484f9e4fd5586dca7c20403dc80d61dbe682a436b4d15d10bc0003a5e748513b75e34d9db61c6fd0fa55533e8424d88fbe6cda8e7cf61d50cb9467192a5cbd47b14b205b38123ad4b7c39d6ce7d6bf02c4a1452d135dc29fc83ef600049e4cd56e3c2e0cfc4cc831bc4ec54410590c15b4b20b63cc91be3436a4d09c0c22be4ab96962ad6e94d83e14c770e122aebae6fdbdea97f98cec7da5d30ed2a40106a7565c6387a700e02ee09652b40bdeef044441ca1e3b3c9376d4a129d22ca861501c3f5c0e8469c9a0e5d1b09d9f84c6517c0a2b400c0b47552006fff1dad3a5000a4db87004c483f899b5fd766c14334dfb5ca2fa5698964cf9644669b325bd3485207cbc4180a360023d1412da68bb11a0a82fee70a6bf03dda30b7aae53e0e465010ba3a6e45c9d8ef1d1041fdc7a926a9f41075531d45824144bbc720d111ee7270a77dd6dd65558b30d0f03692e075bd7d96cdfb24f5a68fecc22e441ded230c9cc010c09380e394e2b30fd036f13152b115dab7a206270d52255dfbbf0505c67bf510e70d0a6075f9bae19235eaf8a0893a4af9ed0df1b8cd67e1fe7b2ec61178d3ca4010dc491600d07d10a6468fb5955d94bc114efab46104e2ae530931231fea52cf7e32964a1c8bfe0ee38aaa8abfe8edcb7c079b6dd97b2c317c9d71cb5973bb53c72010f787e3c59ac484fdca7d5e41b29cebee08cb1789d61a0f29ccd0353118fd667ab1473a626eb6c237cff70ffb1eb2a556862197b08f183d5852168f5ce0f92632b0110f7ee4abdedc936ebebe86b3493292a9fa6625ab910b4a1340b46478a819508d1261f3d559d5cc95dead635c215b80b1cb2df348639d1ca572d3d14f07dc38908011103e3cdc9936ffbb7c0af5d77a4c092c5c42de161c9254919d19af718defd71a757fcbb1e3772e72c3a8c8291ab36f628a060030abf8ffb43923bb1a05cf9605d0112ddea2ce8ec77b9e222db5f1a95861c3da2ed3f54f7e937008bcc14b2458b98990eeb5910c7e9b2a27ff47a9568d0a3fedc12f357323905cbc8a1be6acbc5986b0064c37bca00000000001af8cd23c2ab91237730770bbea08d61005cdda0984348f3f6eecb559638c0bba0000000002144b1420150325748000300010001020005009d2efa1235ab86c0935cb424b102be4f217e74d1109df9e75dfa8338fc0f0908782f95862b045670cd22bee3114c39763a4a08beeb663b145d283c31d7d1101c4f000000059cc51c400000000000e4e1bffffffff8000000059b3f3c700000000000eae895010000001a0000001e0000000064c37bca0000000064c37bca0000000064c37bc9000000059cc51c400000000000e4e1bf0000000064c37bc948d6033d733e27950c2e0351e2505491cd9154824f716d9513514c74b9f98f583dd2b63686a450ec7290df3a1e0b583c0481f651351edfa7636f39aed55cf8a300000005a7462c060000000000d206a2fffffff800000005a5c499380000000000f44b7d010000001c000000200000000064c37bca0000000064c37bca0000000064c37bc900000005a74653cc0000000000d1dedc0000000064c37bc83515b3861e8fe93e5f540ba4077c216404782b86d5e78077b3cbfd27313ab3bce62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43000002a724c9d1000000000032396fc5fffffff8000002a6e3e0fec0000000002ee4815c010000001b000000200000000064c37bca0000000064c37bca0000000064c37bc9000002a724c9d1000000000032396fc50000000064c37bc99b5f73e0075e7d70376012180ddba94272f68d85eae4104e335561c982253d41a19d04ac696c7a6616d291c7e5d1377cc8be437c327b75adb5dc1bad745fcae800000000045152eb000000000001bb63fffffff800000000044de0b500000000000185df0100000015000000160000000064c37bca0000000064c37bca0000000064c37bc900000000045152eb000000000001bb630000000064c37bc8e876fcd130add8984a33aab52af36bc1b9f822c9ebe376f3aa72d630974e15f0dcef50dd0a4cd2dcc17e45df1676dcb336a11a61c69df7a0299b0150c672d25c000000000074990500000000000011d9fffffff80000000000748c2f000000000000116f010000001b000000200000000064c37bca0000000064c37bca0000000064c37bc900000000007498d400000000000011a80000000064c37bc9"
BASE64_VAA = "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"
ACCUMULATOR_UPDATE_DATA = "UE5BVQEAAAADuAEAAAADDQAsKPsmb7Vz7io3taJQKgoi1m/z0kqKgtpmlkv+ZuunX2Iegsf+8fuUtpHPLKgCWPU8PN2x9NyAZz5BY9M3SWwJAALYlM0U7f2GFWfEjKwSJlHZ5sf+n6KXCocVC66ImS2o0TD0SBhTWcp0KdcuzR1rY1jfIHaFpVneroRLbTjNrk/WAAMuAYxPVPf1DR30wYQo12Dbf+in3akTjhKERNQ+nPwRjxAyIQD+52LU3Rh2VL7nOIStMNTiBMaiWHywaPoXowWAAQbillhhX4MR+7h81PfxHIbiXBmER4c5M7spilWKkROb+VXhrqnVJL162t9TdhYk56PDIhvXO1Tm/ldjVJw130y0AAk6qpccfsxDZEmVN8LI4z8739Ni/kb+CB3yW2l2dWhKTjBeNanhK6TCCoNH/jRzWfrjrEk5zjNrUr82JwL4fR1OAQrYZescxbH26m8QHiH+RHzwlXpUKJgbHD5NnWtB7oFb9AFM15jbjd4yIEBEtAlXPE0Q4j+X+DLnCtZbLSQiYNh5AQvz70LTbYry1lEExuUcO+IRJiysw5AFyqZ9Y1E//WKIqgEysfcnHwoOxtDtAc5Z9sTUEYfPqQ1d27k3Yk0X7dvCAQ10cdG0qYHb+bQrYRIKKnb0aeCjkCs0HZQY2fXYmimyfTNfECclmPW9k+CfOvW0JKuFxC1l11zJ3zjsgN/peA8BAQ5oIFQGjq9qmf5gegE1DjuzXsGksKao6nsjTXYIspCczCe2h5KNQ9l5hws11hauUKS20JoOYjHwxPD2x0adJKvkAQ+4UjVcZgVEQP8y3caqUDH81Ikcadz2bESpYg93dpnzZTH6A7Ue+RL34PTNx6cCRzukwQuhiStuyL1WYEIrLI4nABAjGv3EBXjWaPLUj59OzVnGkzxkr6C4KDjMmpsYNzx7I2lp2iQV46TM78El8i9h7twiEDUOSdC5CmfQjRpkP72yABGVAQELUm2/SjkpF0O+/rVDgA/Y2/wMacD1ZDahdyvSNSFThn5NyRYA1JXGgIDxoYeAZgkr1gL1cjCLWiO+Bs9QARIiCvHfIkn2aYhYHQq/u6cHB/2DxE3OgbCZyTv8OVO55hQDkJ1gDwAec+IJ4M5Od4OxWEu+OywhJT7zUmwZko9MAGTeJ+kAAAAAABrhAfrtrFhR4yubI7X5QRqMK6xKrj7U3XuBHdGnLqSqcQAAAAAAWllxAUFVV1YAAAAAAAVZ/XAAACcQ8Xfx5wQ+nj1rn6IeTUAy+VER1nUBAFUA5i32yLSoX+GmfbRNwS3l2zMPesZrctxliv7fD0pBW0MAAAKUUTJXzwAAAADDrAZ1////+AAAAABk3ifoAAAAAGTeJ+cAAAKWepR2oAAAAAC/b8SsCasjFzENKvXWwOycuzCVaDWfm0IuuuesmamDKl2lNXss15orlNN+xHVNEEIIq7Xg8GRZGVLt43fkg7xli6EPQ/Nyxl6SixiYteNt1uTTh4M1lQTUjPxKnkE5JEea4RnhOWgmSAWMf8ft4KgE7hvRifV1JP0rOsNgsOYFRbs6iDKW1qLpxgZLMAiOclwS3Tjw2hj8sPfq1NHeVttsBEK5SIM14GjAuD/p2V0+NqHqMHxU/kfftg=="
ACCUMULATOR_VAA = "AQAAAAMNACwo+yZvtXPuKje1olAqCiLWb/PSSoqC2maWS/5m66dfYh6Cx/7x+5S2kc8sqAJY9Tw83bH03IBnPkFj0zdJbAkAAtiUzRTt/YYVZ8SMrBImUdnmx/6fopcKhxULroiZLajRMPRIGFNZynQp1y7NHWtjWN8gdoWlWd6uhEttOM2uT9YAAy4BjE9U9/UNHfTBhCjXYNt/6KfdqROOEoRE1D6c/BGPEDIhAP7nYtTdGHZUvuc4hK0w1OIExqJYfLBo+hejBYABBuKWWGFfgxH7uHzU9/EchuJcGYRHhzkzuymKVYqRE5v5VeGuqdUkvXra31N2FiTno8MiG9c7VOb+V2NUnDXfTLQACTqqlxx+zENkSZU3wsjjPzvf02L+Rv4IHfJbaXZ1aEpOMF41qeErpMIKg0f+NHNZ+uOsSTnOM2tSvzYnAvh9HU4BCthl6xzFsfbqbxAeIf5EfPCVelQomBscPk2da0HugVv0AUzXmNuN3jIgQES0CVc8TRDiP5f4MucK1lstJCJg2HkBC/PvQtNtivLWUQTG5Rw74hEmLKzDkAXKpn1jUT/9YoiqATKx9ycfCg7G0O0Bzln2xNQRh8+pDV3buTdiTRft28IBDXRx0bSpgdv5tCthEgoqdvRp4KOQKzQdlBjZ9diaKbJ9M18QJyWY9b2T4J869bQkq4XELWXXXMnfOOyA3+l4DwEBDmggVAaOr2qZ/mB6ATUOO7NewaSwpqjqeyNNdgiykJzMJ7aHko1D2XmHCzXWFq5QpLbQmg5iMfDE8PbHRp0kq+QBD7hSNVxmBURA/zLdxqpQMfzUiRxp3PZsRKliD3d2mfNlMfoDtR75Evfg9M3HpwJHO6TBC6GJK27IvVZgQissjicAECMa/cQFeNZo8tSPn07NWcaTPGSvoLgoOMyamxg3PHsjaWnaJBXjpMzvwSXyL2Hu3CIQNQ5J0LkKZ9CNGmQ/vbIAEZUBAQtSbb9KOSkXQ77+tUOAD9jb/AxpwPVkNqF3K9I1IVOGfk3JFgDUlcaAgPGhh4BmCSvWAvVyMItaI74Gz1ABEiIK8d8iSfZpiFgdCr+7pwcH/YPETc6BsJnJO/w5U7nmFAOQnWAPAB5z4gngzk53g7FYS747LCElPvNSbBmSj0wAZN4n6QAAAAAAGuEB+u2sWFHjK5sjtflBGowrrEquPtTde4Ed0acupKpxAAAAAABaWXEBQVVXVgAAAAAABVn9cAAAJxDxd/HnBD6ePWufoh5NQDL5URHWdQ=="


def test_valid_hex_vaa_to_price_info():
    price_info = vaa_to_price_info(ID, HEX_VAA)
    assert price_info.seq_num == 558149954
    assert price_info.vaa == HEX_VAA
    assert price_info.publish_time == 1690532810
    assert price_info.attestation_time == 1690532810
    assert price_info.last_attested_publish_time == 1690532809
    assert price_info.price_feed.ema_price.price == "2915811000000"
    assert price_info.price_feed.ema_price.conf == "786727260"
    assert price_info.price_feed.ema_price.expo == -8
    assert price_info.price_feed.ema_price.publish_time == 1690532810
    assert price_info.price_feed.id == ID
    assert price_info.price_feed.price.price == "2916900000000"
    assert price_info.price_feed.price.conf == "842624965"
    assert price_info.price_feed.price.expo == -8
    assert price_info.price_feed.price.publish_time == 1690532810
    assert price_info.emitter_chain_id == 26


def test_valid_base64_vaa_to_price_info():
    price_info = vaa_to_price_info(ID, BASE64_VAA, "base64")
    assert price_info.seq_num == 558149954
    assert price_info.vaa == BASE64_VAA
    assert price_info.publish_time == 1690532810
    assert price_info.attestation_time == 1690532810
    assert price_info.last_attested_publish_time == 1690532809
    assert price_info.price_feed.ema_price.price == "2915811000000"
    assert price_info.price_feed.ema_price.conf == "786727260"
    assert price_info.price_feed.ema_price.expo == -8
    assert price_info.price_feed.ema_price.publish_time == 1690532810
    assert price_info.price_feed.id == ID
    assert price_info.price_feed.price.price == "2916900000000"
    assert price_info.price_feed.price.conf == "842624965"
    assert price_info.price_feed.price.expo == -8
    assert price_info.price_feed.price.publish_time == 1690532810
    assert price_info.emitter_chain_id == 26


def test_invalid_vaa_to_price_info():
    try:
        vaa_to_price_info(ID, HEX_VAA + "10")
    except ValueError as ve:
        assert ve.args[0] == "Invalid length: 801, expected: 800"


def test_encode_vaa_for_chain():
    # Test that encoding a hex VAA as hex returns the same hex VAA
    encoded_vaa = encode_vaa_for_chain(HEX_VAA, "hex")
    assert encoded_vaa == HEX_VAA

    # Test that encoding a HEX VAA as base64 returns base64 VAA
    encoded_vaa = encode_vaa_for_chain(HEX_VAA, "base64")
    assert encoded_vaa == BASE64_VAA

    # Test that encoding a base64 VAA as base64 returns the same base64 VAA
    encoded_vaa = encode_vaa_for_chain(BASE64_VAA, "base64")
    assert encoded_vaa == BASE64_VAA

    # Test that encoding a base64 VAA as hex returns hex VAA
    encoded_vaa = encode_vaa_for_chain(BASE64_VAA, "hex")
    assert encoded_vaa == HEX_VAA


def test_valid_accumulator_vaa_to_price_info():
    price_info = vaa_to_price_info(ID, ACCUMULATOR_UPDATE_DATA, "base64")
    assert price_info.seq_num == 5921137
    assert price_info.vaa == ACCUMULATOR_VAA
    assert price_info.publish_time == 1692280808
    assert price_info.attestation_time == 1692280808
    assert price_info.last_attested_publish_time == 1692280807
    assert price_info.price_feed.ema_price.price == "2845324900000"
    assert price_info.price_feed.ema_price.conf == "3211773100"
    assert price_info.price_feed.ema_price.expo == -8
    assert price_info.price_feed.ema_price.publish_time == 1692280808
    assert price_info.price_feed.id == ID
    assert price_info.price_feed.price.price == "2836040669135"
    assert price_info.price_feed.price.conf == "3282830965"
    assert price_info.price_feed.price.expo == -8
    assert price_info.price_feed.price.publish_time == 1692280808
    assert price_info.emitter_chain_id == 26
