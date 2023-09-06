import base64

from pythclient.price_feeds import (
    ACCUMULATOR_MAGIC,
    AccumulatorUpdate,
    MerkleUpdate,
    compress_accumulator_update,
    encode_vaa_for_chain,
    is_accumulator_update,
    parse_accumulator_update,
    serialize_accumulator_update,
    vaa_to_price_info,
    vaa_to_price_infos,
)

BTC_ID = "e62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43"  # BTC/USD
ETH_ID = "ff61491a931112ddf1bd8147cd1b641375f79f5825126d665480874634fd0ace"  # ETH/USD
SOL_ID = "ef0d8b6fda2ceba41da15d4095d1da392a0d2f8ed0c6c7bc0f4cfac8c280b56d"  # SOL/USD
HEX_VAA = "01000000030d00ca037dde1419ea373de7474bff80268e41f55e84dd8e4fa5e5167808111e63e4064efcfd93075d9d162090bc478a017603ef56c4d26e0c46e0af6128c08984470002e9abd7c4e62bbc6b453c5ca014b7313bbadb17d6443190d6679b7c0ccb03bae619d21dcb5d6d5a484f9e4fd5586dca7c20403dc80d61dbe682a436b4d15d10bc0003a5e748513b75e34d9db61c6fd0fa55533e8424d88fbe6cda8e7cf61d50cb9467192a5cbd47b14b205b38123ad4b7c39d6ce7d6bf02c4a1452d135dc29fc83ef600049e4cd56e3c2e0cfc4cc831bc4ec54410590c15b4b20b63cc91be3436a4d09c0c22be4ab96962ad6e94d83e14c770e122aebae6fdbdea97f98cec7da5d30ed2a40106a7565c6387a700e02ee09652b40bdeef044441ca1e3b3c9376d4a129d22ca861501c3f5c0e8469c9a0e5d1b09d9f84c6517c0a2b400c0b47552006fff1dad3a5000a4db87004c483f899b5fd766c14334dfb5ca2fa5698964cf9644669b325bd3485207cbc4180a360023d1412da68bb11a0a82fee70a6bf03dda30b7aae53e0e465010ba3a6e45c9d8ef1d1041fdc7a926a9f41075531d45824144bbc720d111ee7270a77dd6dd65558b30d0f03692e075bd7d96cdfb24f5a68fecc22e441ded230c9cc010c09380e394e2b30fd036f13152b115dab7a206270d52255dfbbf0505c67bf510e70d0a6075f9bae19235eaf8a0893a4af9ed0df1b8cd67e1fe7b2ec61178d3ca4010dc491600d07d10a6468fb5955d94bc114efab46104e2ae530931231fea52cf7e32964a1c8bfe0ee38aaa8abfe8edcb7c079b6dd97b2c317c9d71cb5973bb53c72010f787e3c59ac484fdca7d5e41b29cebee08cb1789d61a0f29ccd0353118fd667ab1473a626eb6c237cff70ffb1eb2a556862197b08f183d5852168f5ce0f92632b0110f7ee4abdedc936ebebe86b3493292a9fa6625ab910b4a1340b46478a819508d1261f3d559d5cc95dead635c215b80b1cb2df348639d1ca572d3d14f07dc38908011103e3cdc9936ffbb7c0af5d77a4c092c5c42de161c9254919d19af718defd71a757fcbb1e3772e72c3a8c8291ab36f628a060030abf8ffb43923bb1a05cf9605d0112ddea2ce8ec77b9e222db5f1a95861c3da2ed3f54f7e937008bcc14b2458b98990eeb5910c7e9b2a27ff47a9568d0a3fedc12f357323905cbc8a1be6acbc5986b0064c37bca00000000001af8cd23c2ab91237730770bbea08d61005cdda0984348f3f6eecb559638c0bba0000000002144b1420150325748000300010001020005009d2efa1235ab86c0935cb424b102be4f217e74d1109df9e75dfa8338fc0f0908782f95862b045670cd22bee3114c39763a4a08beeb663b145d283c31d7d1101c4f000000059cc51c400000000000e4e1bffffffff8000000059b3f3c700000000000eae895010000001a0000001e0000000064c37bca0000000064c37bca0000000064c37bc9000000059cc51c400000000000e4e1bf0000000064c37bc948d6033d733e27950c2e0351e2505491cd9154824f716d9513514c74b9f98f583dd2b63686a450ec7290df3a1e0b583c0481f651351edfa7636f39aed55cf8a300000005a7462c060000000000d206a2fffffff800000005a5c499380000000000f44b7d010000001c000000200000000064c37bca0000000064c37bca0000000064c37bc900000005a74653cc0000000000d1dedc0000000064c37bc83515b3861e8fe93e5f540ba4077c216404782b86d5e78077b3cbfd27313ab3bce62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43000002a724c9d1000000000032396fc5fffffff8000002a6e3e0fec0000000002ee4815c010000001b000000200000000064c37bca0000000064c37bca0000000064c37bc9000002a724c9d1000000000032396fc50000000064c37bc99b5f73e0075e7d70376012180ddba94272f68d85eae4104e335561c982253d41a19d04ac696c7a6616d291c7e5d1377cc8be437c327b75adb5dc1bad745fcae800000000045152eb000000000001bb63fffffff800000000044de0b500000000000185df0100000015000000160000000064c37bca0000000064c37bca0000000064c37bc900000000045152eb000000000001bb630000000064c37bc8e876fcd130add8984a33aab52af36bc1b9f822c9ebe376f3aa72d630974e15f0dcef50dd0a4cd2dcc17e45df1676dcb336a11a61c69df7a0299b0150c672d25c000000000074990500000000000011d9fffffff80000000000748c2f000000000000116f010000001b000000200000000064c37bca0000000064c37bca0000000064c37bc900000000007498d400000000000011a80000000064c37bc9"
BASE64_VAA = "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"
ACCUMULATOR_UPDATE_SAME_VAA = "AQAAAAMNAFpq7E0Obvl72gKby+ppmEI5Z8mRvVKEspd5WJR8J59qYeYtb1/INY9IwAOKHMFs1c2X+K+4PHLl73+VboKgAdcBAQRPIzGyOezZIEyn8HQnPC4WpFHey1mBSgBAJwT/HtbkMk6N5Ffguk7zZ0A5+wTfX0TZLmO9ssLbA5lwDhLQ5y4BAqSpGBxCk7j9taLP29magR9tAMH4DWP6YRDMp+rSecIqYbcR3EGhNQrweVmxuigi7edrkGzqpzapjJ9cr0uWyzAAA1UBZ+B7yxvzBK5uPNX7H/6ru9/5ZAQlyji0gHXZhQzSFn+MfT003KQh9CPe1lmnwbtq3O+9YppdoaPhOGYMc6EABPyfLBNBRtWjodqDO+YjiN5sTWZEr5P6N2LmbiXsnq0hdg/1TObwjlm8y46E3LqMjvcRkDujt5EkDhz6SGBKcC0BC25XVEhmrUE5Y9tUCsUlJr3gFMf53UW1BMBevcmaHEd8AbBDlSvsmj3U6crs661/8G5Cd78G1O+q/yTV8T0OP6EADBtAjSGE/ALSb9eCypqC4QZFhyophpLX3kHCtApLBT8Wf76M3v9E6Tr9lSvPjn0p5BmNQeuOkvbcT6lYbOtUc8EADZH0nP141ClY9whc8W5wiSsR+LxOatxXeMiMrBWOzcJKfdw8oi6MImVNUwGjjSFqWFu/+sgEErcUjMRPLgBbJToBDp1uhbpKhxmoXkwz7uPesMHeCBVQ2Xb3Bijdfg9KtLypNAtOKmUhhOo5fGpiesg6EK2x/Sz73GHR3yFNvdifBmABD6Blheynt9vUTVPubXNKtTlsGuRNUE5V/+Y0uNZv3DhWUtZZ1RA9EjIT8VQG1KQEXkwO3BtcnvAiyT5huZNaoisBECqLp6ajYNUmPadPDCWf1XiRfhrEvXspJ7WAgxh9rmqaZ5IN2MzPzH3az0zKyk5reHASDVo/yLAvT0et9apsgt8BEdor5LY5cD4WVAXljiZsQA8tmyJij+RH5NkZT9wO5w5aHKjhMDVpqgKteksZDdTZC9IxSlkCQ13eAKN4rNuPv0IBEs6lIQpssitiLPQb6KLnLa9UxyMEJGz4arZwb9EFGVehS3WG6sFqRRPU9W4jcvcNGVsBVhuzmkvv3u9MDJuIzUwBZPEpgQAAAAAAGuEB+u2sWFHjK5sjtflBGowrrEquPtTde4Ed0acupKpxAAAAAACKOWQBQVVXVgAAAAAABYq9dAAAJxDIoeJ4YgtzgZ2ikt9+LNjv29G4yg=="
ACCUMULATOR_UPDATE_DATA_BTC_SAME_VAA = "UE5BVQEAAAADuAEAAAADDQBaauxNDm75e9oCm8vqaZhCOWfJkb1ShLKXeViUfCefamHmLW9fyDWPSMADihzBbNXNl/ivuDxy5e9/lW6CoAHXAQEETyMxsjns2SBMp/B0JzwuFqRR3stZgUoAQCcE/x7W5DJOjeRX4LpO82dAOfsE319E2S5jvbLC2wOZcA4S0OcuAQKkqRgcQpO4/bWiz9vZmoEfbQDB+A1j+mEQzKfq0nnCKmG3EdxBoTUK8HlZsbooIu3na5Bs6qc2qYyfXK9LlsswAANVAWfge8sb8wSubjzV+x/+q7vf+WQEJco4tIB12YUM0hZ/jH09NNykIfQj3tZZp8G7atzvvWKaXaGj4ThmDHOhAAT8nywTQUbVo6HagzvmI4jebE1mRK+T+jdi5m4l7J6tIXYP9Uzm8I5ZvMuOhNy6jI73EZA7o7eRJA4c+khgSnAtAQtuV1RIZq1BOWPbVArFJSa94BTH+d1FtQTAXr3JmhxHfAGwQ5Ur7Jo91OnK7Outf/BuQne/BtTvqv8k1fE9Dj+hAAwbQI0hhPwC0m/XgsqaguEGRYcqKYaS195BwrQKSwU/Fn++jN7/ROk6/ZUrz459KeQZjUHrjpL23E+pWGzrVHPBAA2R9Jz9eNQpWPcIXPFucIkrEfi8TmrcV3jIjKwVjs3CSn3cPKIujCJlTVMBo40halhbv/rIBBK3FIzETy4AWyU6AQ6dboW6SocZqF5MM+7j3rDB3ggVUNl29wYo3X4PSrS8qTQLTiplIYTqOXxqYnrIOhCtsf0s+9xh0d8hTb3YnwZgAQ+gZYXsp7fb1E1T7m1zSrU5bBrkTVBOVf/mNLjWb9w4VlLWWdUQPRIyE/FUBtSkBF5MDtwbXJ7wIsk+YbmTWqIrARAqi6emo2DVJj2nTwwln9V4kX4axL17KSe1gIMYfa5qmmeSDdjMz8x92s9MyspOa3hwEg1aP8iwL09HrfWqbILfARHaK+S2OXA+FlQF5Y4mbEAPLZsiYo/kR+TZGU/cDucOWhyo4TA1aaoCrXpLGQ3U2QvSMUpZAkNd3gCjeKzbj79CARLOpSEKbLIrYiz0G+ii5y2vVMcjBCRs+Gq2cG/RBRlXoUt1hurBakUT1PVuI3L3DRlbAVYbs5pL797vTAybiM1MAWTxKYEAAAAAABrhAfrtrFhR4yubI7X5QRqMK6xKrj7U3XuBHdGnLqSqcQAAAAAAijlkAUFVV1YAAAAAAAWKvXQAACcQyKHieGILc4GdopLffizY79vRuMoBAFUA5i32yLSoX+GmfbRNwS3l2zMPesZrctxliv7fD0pBW0MAAAJb3eCW3wAAAAA8JOwR////+AAAAABk8SmAAAAAAGTxKYAAAAJdBwk84AAAAAA9yJiiCbEdXozpxwFJH1HPYYuRd8HhJRDnW9MncEdkxFG+r+dTKQQxM9w8mXLRd/UWCyaHZYHtjTTArEV3OaVMoedGhGHHMyXwx/nyPWRdsFJkxbMwp5vP1Kg0XG4o5lxmJgsbtFRfX8pfNTgClepaPpyD53afOdLk/yN6Gd6fiq01xIhclaBw4kFKPrK2AuHy3Tjw2hj8sPfq1NHeVttsBEK5SIO7rH9+iA9g386g9frxjnyxLscgUw=="
ACCUMULATOR_UPDATE_BTC_MESSAGE = "AOYt9si0qF/hpn20TcEt5dszD3rGa3LcZYr+3w9KQVtDAAACW93glt8AAAAAPCTsEf////gAAAAAZPEpgAAAAABk8SmAAAACXQcJPOAAAAAAPciYog=="
ACCUMULATOR_UPDATE_BTC_PROOF = [
    "sR1ejOnHAUkfUc9hi5F3weElEOc=",
    "W9MncEdkxFG+r+dTKQQxM9w8mXI=",
    "0Xf1Fgsmh2WB7Y00wKxFdzmlTKE=",
    "50aEYcczJfDH+fI9ZF2wUmTFszA=",
    "p5vP1Kg0XG4o5lxmJgsbtFRfX8o=",
    "XzU4ApXqWj6cg+d2nznS5P8jehk=",
    "3p+KrTXEiFyVoHDiQUo+srYC4fI=",
    "3Tjw2hj8sPfq1NHeVttsBEK5SIM=",
    "u6x/fogPYN/OoPX68Y58sS7HIFM=",
]
ACCUMULATOR_UPDATE_DATA_ETH_SAME_VAA = "UE5BVQEAAAADuAEAAAADDQBaauxNDm75e9oCm8vqaZhCOWfJkb1ShLKXeViUfCefamHmLW9fyDWPSMADihzBbNXNl/ivuDxy5e9/lW6CoAHXAQEETyMxsjns2SBMp/B0JzwuFqRR3stZgUoAQCcE/x7W5DJOjeRX4LpO82dAOfsE319E2S5jvbLC2wOZcA4S0OcuAQKkqRgcQpO4/bWiz9vZmoEfbQDB+A1j+mEQzKfq0nnCKmG3EdxBoTUK8HlZsbooIu3na5Bs6qc2qYyfXK9LlsswAANVAWfge8sb8wSubjzV+x/+q7vf+WQEJco4tIB12YUM0hZ/jH09NNykIfQj3tZZp8G7atzvvWKaXaGj4ThmDHOhAAT8nywTQUbVo6HagzvmI4jebE1mRK+T+jdi5m4l7J6tIXYP9Uzm8I5ZvMuOhNy6jI73EZA7o7eRJA4c+khgSnAtAQtuV1RIZq1BOWPbVArFJSa94BTH+d1FtQTAXr3JmhxHfAGwQ5Ur7Jo91OnK7Outf/BuQne/BtTvqv8k1fE9Dj+hAAwbQI0hhPwC0m/XgsqaguEGRYcqKYaS195BwrQKSwU/Fn++jN7/ROk6/ZUrz459KeQZjUHrjpL23E+pWGzrVHPBAA2R9Jz9eNQpWPcIXPFucIkrEfi8TmrcV3jIjKwVjs3CSn3cPKIujCJlTVMBo40halhbv/rIBBK3FIzETy4AWyU6AQ6dboW6SocZqF5MM+7j3rDB3ggVUNl29wYo3X4PSrS8qTQLTiplIYTqOXxqYnrIOhCtsf0s+9xh0d8hTb3YnwZgAQ+gZYXsp7fb1E1T7m1zSrU5bBrkTVBOVf/mNLjWb9w4VlLWWdUQPRIyE/FUBtSkBF5MDtwbXJ7wIsk+YbmTWqIrARAqi6emo2DVJj2nTwwln9V4kX4axL17KSe1gIMYfa5qmmeSDdjMz8x92s9MyspOa3hwEg1aP8iwL09HrfWqbILfARHaK+S2OXA+FlQF5Y4mbEAPLZsiYo/kR+TZGU/cDucOWhyo4TA1aaoCrXpLGQ3U2QvSMUpZAkNd3gCjeKzbj79CARLOpSEKbLIrYiz0G+ii5y2vVMcjBCRs+Gq2cG/RBRlXoUt1hurBakUT1PVuI3L3DRlbAVYbs5pL797vTAybiM1MAWTxKYEAAAAAABrhAfrtrFhR4yubI7X5QRqMK6xKrj7U3XuBHdGnLqSqcQAAAAAAijlkAUFVV1YAAAAAAAWKvXQAACcQyKHieGILc4GdopLffizY79vRuMoBAFUA/2FJGpMREt3xvYFHzRtkE3X3n1glEm1mVICHRjT9Cs4AAAAmUE1Q3AAAAAAFW9d5////+AAAAABk8SmAAAAAAGTxKX8AAAAmVojMOAAAAAAFhbrjCf0FL/Gh8P02OPw0rSRrwrAE7A5nqKEYAXfPMLLAvruxrf6PeYXQUdIFoB4lBNnwwG5+fLDPJBFgmMogKsX2reLo9aEuwAaxbUa+HwIouU2VjNCBJX5Kvy+9aUPnDPtrCDVCDN4wkHiRIOOTArEqEzDwXI9xwPWog2gG2pbBnq7ut8UB/5xxi/Kgg1Cb3Tjw2hj8sPfq1NHeVttsBEK5SIO7rH9+iA9g386g9frxjnyxLscgUw=="
ACCUMULATOR_UPDATE_DIFFERENT_VAA = "AQAAAAMNAEoUCbmBnFBnz08OS1e8Id7uQPShgJTRh8QR4ywcnghBbwDmDSp7TARIgYpwRwDo4+JzXYMTW12npgBGC+IikUYBAf7Uub70p3/2srHQTFDwC22vb5yXHgie/l8JRICYtKh5fzk7OzxiwAJ56chOMtfmW4pI1aCbbVa70BqO+BRIrIMAAnvoDBeZbaknaBrZmmJARECvq/rpUzkyu+OnlSJ7CZJtW//uR/fIzYBGvpamlsG+fBV2mc38l1AVGiYCX2ZlL9IAA08KRaKnOiz6KhYTlnOT7E7XSSZHuws9a9qUY6Oo8yMmV3x3F83rpBWpi9Ugo11CDJ9woosSd/DU8pjWXKM+5iMBBIrblxVY0LxqTJxEqGNrCg/RtoX3G1stadhIAUGCImOeUd2VcEQdislbuYHVvoAuOCUyQRdysJmxFQulaBC0xvIBCzXee/DnTZwxUVhcHovzZHk1xjIfherjBbVFr7HzoH5kJGDK+4f4As/ePX+IDw5sHjd6SLnmHzckg1TI+LJJOxsBDDWviC0qacCYq0rgZ7x76InITHDDmG4rjyeqVZBkEExzEi7RpBkNk7ftixprqNsfLpiC8yfWIfOHyt4fa99L+XIBDUdUI9LOtO06MXdkXwEmoZZ502F2d9/K9EjSD0RapBG9eg/DLvD/jWOd8pSvFyuEalHNw262Vs8032Q+2ZQSrmAADhDAWGo0+rNbL+FjaqndEYeNXyL3PHgjRonI6Ls0H7V7CabfI5mTie8GqLMYG3F0UohM1qDQ4eHghs7zM43/q+cAD+oGxkSW3LMPL84meqxfyDI5Sbnf+kWJ5drbeVI4M+L2ZhvBIJONvTdfdstWMqqseLvUXn6qVsKp6vvB9c3NKuABEMiE54SyBxZSZ8p96z+Wf05XiLxcApDOUNoLgFFScA7TIg8lkBMTes6r9Rxd0d9BQmIj8EHOH4o1lOLtCy8M/WYAEVktfgaQ/P3ajp4tCujzLVEU2I/XDXIN/RN3s8G0Tzq6MfBBjdCoIenZD2GJWjHuCjXANYQbofSvM4pB8pML2jIAEt3oVv7ZOHKGIW2t7Jz/SUuZJ+LdkKVmILt5U6+DfbJuY21la6d9i7GiNV0zp7cRN4ehnxfOx61pveIErM4ieYQBZPEpgQAAAAAAGuEB+u2sWFHjK5sjtflBGowrrEquPtTde4Ed0acupKpxAAAAAACKOWUBQVVXVgAAAAAABYq9dQAAJxDce8BPBkmE4xdQ6mzGXeOzdwnZSg=="
ACCUMULATOR_UPDATE_DATA_SOL_DIFFERENT_VAA = "UE5BVQEAAAADuAEAAAADDQBKFAm5gZxQZ89PDktXvCHe7kD0oYCU0YfEEeMsHJ4IQW8A5g0qe0wESIGKcEcA6OPic12DE1tdp6YARgviIpFGAQH+1Lm+9Kd/9rKx0ExQ8Attr2+clx4Inv5fCUSAmLSoeX85Ozs8YsACeenITjLX5luKSNWgm21Wu9AajvgUSKyDAAJ76AwXmW2pJ2ga2ZpiQERAr6v66VM5Mrvjp5UiewmSbVv/7kf3yM2ARr6WppbBvnwVdpnN/JdQFRomAl9mZS/SAANPCkWipzos+ioWE5Zzk+xO10kmR7sLPWvalGOjqPMjJld8dxfN66QVqYvVIKNdQgyfcKKLEnfw1PKY1lyjPuYjAQSK25cVWNC8akycRKhjawoP0baF9xtbLWnYSAFBgiJjnlHdlXBEHYrJW7mB1b6ALjglMkEXcrCZsRULpWgQtMbyAQs13nvw502cMVFYXB6L82R5NcYyH4Xq4wW1Ra+x86B+ZCRgyvuH+ALP3j1/iA8ObB43eki55h83JINUyPiySTsbAQw1r4gtKmnAmKtK4Ge8e+iJyExww5huK48nqlWQZBBMcxIu0aQZDZO37Ysaa6jbHy6YgvMn1iHzh8reH2vfS/lyAQ1HVCPSzrTtOjF3ZF8BJqGWedNhdnffyvRI0g9EWqQRvXoPwy7w/41jnfKUrxcrhGpRzcNutlbPNN9kPtmUEq5gAA4QwFhqNPqzWy/hY2qp3RGHjV8i9zx4I0aJyOi7NB+1ewmm3yOZk4nvBqizGBtxdFKITNag0OHh4IbO8zON/6vnAA/qBsZEltyzDy/OJnqsX8gyOUm53/pFieXa23lSODPi9mYbwSCTjb03X3bLVjKqrHi71F5+qlbCqer7wfXNzSrgARDIhOeEsgcWUmfKfes/ln9OV4i8XAKQzlDaC4BRUnAO0yIPJZATE3rOq/UcXdHfQUJiI/BBzh+KNZTi7QsvDP1mABFZLX4GkPz92o6eLQro8y1RFNiP1w1yDf0Td7PBtE86ujHwQY3QqCHp2Q9hiVox7go1wDWEG6H0rzOKQfKTC9oyABLd6Fb+2ThyhiFtreyc/0lLmSfi3ZClZiC7eVOvg32ybmNtZWunfYuxojVdM6e3ETeHoZ8Xzsetab3iBKzOInmEAWTxKYEAAAAAABrhAfrtrFhR4yubI7X5QRqMK6xKrj7U3XuBHdGnLqSqcQAAAAAAijllAUFVV1YAAAAAAAWKvXUAACcQ3HvATwZJhOMXUOpsxl3js3cJ2UoBAFUA7w2Lb9os66QdoV1AldHaOSoNL47Qxse8D0z6yMKAtW0AAAAAdZyz4QAAAAAAGzQd////+AAAAABk8SmBAAAAAGTxKYAAAAAAdajBegAAAAAAGDQdCX7POyhhbRE0fZPLbyONUAJ+6eS8CUz89ZmOaX9iCON0AzYTqrcpKZe189sKyhdvV8wZPkdHj8K7sNCWVP77y4K8q0eIHSbEbiAZv3GQxptsAP/yBqn4QmvmKA8tqiNp2ZwyMvTreSVyWhDVPo+acVFaI5WQHw45KwMm3/L7zcEKr8+pzQl8FKfnH1wy3Tjw2hj8sPfq1NHeVttsBEK5SIPSXMgExPoP1vmy7SymxxR8JIM3ug=="


def test_is_accumulator_update():
    # Test that a price service VAA is not an accumulator update
    assert is_accumulator_update(HEX_VAA, "hex") == False
    # Test that an accumulator update VAA is an accumulator update
    assert is_accumulator_update(ACCUMULATOR_UPDATE_DATA_BTC_SAME_VAA, "base64") == True


def test_valid_hex_vaa_to_price_info():
    price_info = vaa_to_price_info(BTC_ID, HEX_VAA)
    assert price_info.seq_num == 558149954
    assert price_info.vaa == HEX_VAA
    assert price_info.publish_time == 1690532810
    assert price_info.attestation_time == 1690532810
    assert price_info.last_attested_publish_time == 1690532809
    assert price_info.price_feed.ema_price.price == "2915811000000"
    assert price_info.price_feed.ema_price.conf == "786727260"
    assert price_info.price_feed.ema_price.expo == -8
    assert price_info.price_feed.ema_price.publish_time == 1690532810
    assert price_info.price_feed.id == BTC_ID
    assert price_info.price_feed.price.price == "2916900000000"
    assert price_info.price_feed.price.conf == "842624965"
    assert price_info.price_feed.price.expo == -8
    assert price_info.price_feed.price.publish_time == 1690532810
    assert price_info.emitter_chain_id == 26


def test_valid_base64_vaa_to_price_info():
    price_info = vaa_to_price_info(BTC_ID, BASE64_VAA, "base64")
    assert price_info.seq_num == 558149954
    assert price_info.vaa == BASE64_VAA
    assert price_info.publish_time == 1690532810
    assert price_info.attestation_time == 1690532810
    assert price_info.last_attested_publish_time == 1690532809
    assert price_info.price_feed.ema_price.price == "2915811000000"
    assert price_info.price_feed.ema_price.conf == "786727260"
    assert price_info.price_feed.ema_price.expo == -8
    assert price_info.price_feed.ema_price.publish_time == 1690532810
    assert price_info.price_feed.id == BTC_ID
    assert price_info.price_feed.price.price == "2916900000000"
    assert price_info.price_feed.price.conf == "842624965"
    assert price_info.price_feed.price.expo == -8
    assert price_info.price_feed.price.publish_time == 1690532810
    assert price_info.emitter_chain_id == 26


def test_invalid_vaa_to_price_info():
    try:
        vaa_to_price_info(BTC_ID, HEX_VAA + "10")
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
    price_info = vaa_to_price_info(
        BTC_ID, ACCUMULATOR_UPDATE_DATA_BTC_SAME_VAA, "base64"
    )
    assert price_info.seq_num == 9058660
    assert price_info.vaa == ACCUMULATOR_UPDATE_SAME_VAA
    assert price_info.publish_time == 1693526400
    assert price_info.attestation_time == 1693526400
    assert price_info.last_attested_publish_time == 1693526400
    assert price_info.price_feed.ema_price.price == "2598573260000"
    assert price_info.price_feed.ema_price.conf == "1036556450"
    assert price_info.price_feed.ema_price.expo == -8
    assert price_info.price_feed.ema_price.publish_time == 1693526400
    assert price_info.price_feed.id == BTC_ID
    assert price_info.price_feed.price.price == "2593587762911"
    assert price_info.price_feed.price.conf == "1009052689"
    assert price_info.price_feed.price.expo == -8
    assert price_info.price_feed.price.publish_time == 1693526400
    assert price_info.emitter_chain_id == 26


def test_parse_accumulator_update():
    parsed_update_data = parse_accumulator_update(
        ACCUMULATOR_UPDATE_DATA_BTC_SAME_VAA, "base64"
    )
    assert parsed_update_data.magic == bytes.fromhex(ACCUMULATOR_MAGIC)
    assert parsed_update_data.major_version == 1
    assert parsed_update_data.minor_version == 0
    assert parsed_update_data.trailing_header_size == 0
    assert parsed_update_data.update_type == 0
    assert parsed_update_data.vaa == base64.b64decode(ACCUMULATOR_UPDATE_SAME_VAA)
    assert parsed_update_data.vaa_length == len(
        base64.b64decode(ACCUMULATOR_UPDATE_SAME_VAA)
    )
    assert parsed_update_data.num_updates == 1
    assert len(parsed_update_data.updates) == 1
    assert parsed_update_data.updates[0].message_size == len(
        base64.b64decode(ACCUMULATOR_UPDATE_BTC_MESSAGE)
    )
    assert parsed_update_data.updates[0].message == base64.b64decode(
        ACCUMULATOR_UPDATE_BTC_MESSAGE
    )
    assert parsed_update_data.updates[0].proof_size == len(
        [base64.b64decode(pr) for pr in ACCUMULATOR_UPDATE_BTC_PROOF]
    )
    assert parsed_update_data.updates[0].proof == [
        base64.b64decode(pr) for pr in ACCUMULATOR_UPDATE_BTC_PROOF
    ]


def test_serialize_accumulator_update():
    magic = bytes.fromhex(ACCUMULATOR_MAGIC)
    major_version = 1
    minor_version = 0
    trailing_header_size = 0
    update_type = 0
    vaa = base64.b64decode(ACCUMULATOR_UPDATE_SAME_VAA)
    vaa_length = len(vaa)
    num_updates = 1
    message = base64.b64decode(ACCUMULATOR_UPDATE_BTC_MESSAGE)
    proof = [base64.b64decode(pr) for pr in ACCUMULATOR_UPDATE_BTC_PROOF]
    updates = [
        MerkleUpdate(
            message_size=len(message),
            message=message,
            proof_size=len(proof),
            proof=proof,
        )
    ]

    update_data = AccumulatorUpdate(
        magic=magic,
        major_version=major_version,
        minor_version=minor_version,
        trailing_header_size=trailing_header_size,
        update_type=update_type,
        vaa_length=vaa_length,
        vaa=vaa,
        num_updates=num_updates,
        updates=updates,
    )
    serialized_update_data = serialize_accumulator_update(update_data, "base64")
    assert serialized_update_data == ACCUMULATOR_UPDATE_DATA_BTC_SAME_VAA


def test_compress_accumulator_update():
    test_data = compress_accumulator_update(
        [ACCUMULATOR_UPDATE_DATA_BTC_SAME_VAA], "base64"
    )
    # Test that compressing 2 accumulator updates with the same vaa returns a single compressed update
    compressed_update_data = compress_accumulator_update(
        [ACCUMULATOR_UPDATE_DATA_BTC_SAME_VAA, ACCUMULATOR_UPDATE_DATA_ETH_SAME_VAA],
        "base64",
    )
    assert len(compressed_update_data) == 1

    # Test that they are the same as the original
    price_infos = vaa_to_price_infos(compressed_update_data[0], "base64")
    for price_info in price_infos:
        assert price_info.seq_num == 9058660
        assert price_info.vaa == ACCUMULATOR_UPDATE_SAME_VAA
        assert price_info.publish_time == 1693526400
        assert price_info.attestation_time == 1693526400
        assert price_info.price_feed.id in [BTC_ID, ETH_ID]
        if price_info.price_feed.id == BTC_ID:
            assert price_info.last_attested_publish_time == 1693526400
            assert price_info.price_feed.ema_price.price == "2598573260000"
            assert price_info.price_feed.ema_price.conf == "1036556450"
            assert price_info.price_feed.ema_price.expo == -8
            assert price_info.price_feed.ema_price.publish_time == 1693526400
            assert price_info.price_feed.price.price == "2593587762911"
            assert price_info.price_feed.price.conf == "1009052689"
            assert price_info.price_feed.price.expo == -8
            assert price_info.price_feed.price.publish_time == 1693526400
        elif price_info.price_feed.id == ETH_ID:
            assert price_info.last_attested_publish_time == 1693526399
            assert price_info.price_feed.ema_price.price == "164660563000"
            assert price_info.price_feed.ema_price.conf == "92650211"
            assert price_info.price_feed.ema_price.expo == -8
            assert price_info.price_feed.ema_price.publish_time == 1693526400
            assert price_info.price_feed.price.price == "164556001500"
            assert price_info.price_feed.price.conf == "89905017"
            assert price_info.price_feed.price.expo == -8
            assert price_info.price_feed.price.publish_time == 1693526400

    # Test that compressing 2 accumulator updates with the same vaa in hex encoding returns a single compressed update
    compressed_update_data = compress_accumulator_update(
        [
            base64.b64decode(ACCUMULATOR_UPDATE_DATA_BTC_SAME_VAA).hex(),
            base64.b64decode(ACCUMULATOR_UPDATE_DATA_ETH_SAME_VAA).hex(),
        ],
        "hex",
    )
    assert len(compressed_update_data) == 1

    # Test that they are the same as the original
    price_infos = vaa_to_price_infos(compressed_update_data[0], "hex")
    for price_info in price_infos:
        assert price_info.seq_num == 9058660
        assert price_info.vaa == base64.b64decode(ACCUMULATOR_UPDATE_SAME_VAA).hex()
        assert price_info.publish_time == 1693526400
        assert price_info.attestation_time == 1693526400
        assert price_info.price_feed.id in [BTC_ID, ETH_ID]
        if price_info.price_feed.id == BTC_ID:
            assert price_info.last_attested_publish_time == 1693526400
            assert price_info.price_feed.ema_price.price == "2598573260000"
            assert price_info.price_feed.ema_price.conf == "1036556450"
            assert price_info.price_feed.ema_price.expo == -8
            assert price_info.price_feed.ema_price.publish_time == 1693526400
            assert price_info.price_feed.price.price == "2593587762911"
            assert price_info.price_feed.price.conf == "1009052689"
            assert price_info.price_feed.price.expo == -8
            assert price_info.price_feed.price.publish_time == 1693526400
        elif price_info.price_feed.id == ETH_ID:
            assert price_info.last_attested_publish_time == 1693526399
            assert price_info.price_feed.ema_price.price == "164660563000"
            assert price_info.price_feed.ema_price.conf == "92650211"
            assert price_info.price_feed.ema_price.expo == -8
            assert price_info.price_feed.ema_price.publish_time == 1693526400
            assert price_info.price_feed.price.price == "164556001500"
            assert price_info.price_feed.price.conf == "89905017"
            assert price_info.price_feed.price.expo == -8
            assert price_info.price_feed.price.publish_time == 1693526400

    # Test that compressing 2 accumulator updates with different vaas returns 2 compressed updates
    compressed_update_data = compress_accumulator_update(
        [
            ACCUMULATOR_UPDATE_DATA_BTC_SAME_VAA,
            ACCUMULATOR_UPDATE_DATA_SOL_DIFFERENT_VAA,
        ],
        "base64",
    )
    assert len(compressed_update_data) == 2

    # Test that they are the same as the original
    price_info = vaa_to_price_info(BTC_ID, compressed_update_data[0], "base64")
    assert price_info.seq_num == 9058660
    assert price_info.vaa == ACCUMULATOR_UPDATE_SAME_VAA
    assert price_info.publish_time == 1693526400
    assert price_info.attestation_time == 1693526400
    assert price_info.last_attested_publish_time == 1693526400
    assert price_info.price_feed.ema_price.price == "2598573260000"
    assert price_info.price_feed.ema_price.conf == "1036556450"
    assert price_info.price_feed.ema_price.expo == -8
    assert price_info.price_feed.ema_price.publish_time == 1693526400
    assert price_info.price_feed.id == BTC_ID
    assert price_info.price_feed.price.price == "2593587762911"
    assert price_info.price_feed.price.conf == "1009052689"
    assert price_info.price_feed.price.expo == -8
    assert price_info.price_feed.price.publish_time == 1693526400
    assert price_info.emitter_chain_id == 26

    price_info = vaa_to_price_info(SOL_ID, compressed_update_data[1], "base64")
    assert price_info.seq_num == 9058661
    assert price_info.vaa == ACCUMULATOR_UPDATE_DIFFERENT_VAA
    assert price_info.publish_time == 1693526401
    assert price_info.attestation_time == 1693526401
    assert price_info.last_attested_publish_time == 1693526400
    assert price_info.price_feed.ema_price.price == "1973993850"
    assert price_info.price_feed.ema_price.conf == "1586205"
    assert price_info.price_feed.ema_price.expo == -8
    assert price_info.price_feed.ema_price.publish_time == 1693526401
    assert price_info.price_feed.id == SOL_ID
    assert price_info.price_feed.price.price == "1973203937"
    assert price_info.price_feed.price.conf == "1782813"
    assert price_info.price_feed.price.expo == -8
    assert price_info.price_feed.price.publish_time == 1693526401
    assert price_info.emitter_chain_id == 26

    # Test that compressing 256 accumulator updates with same vaas returns 2 chunk compressed updates of 255 and 1
    compressed_update_data = compress_accumulator_update(
        [ACCUMULATOR_UPDATE_DATA_BTC_SAME_VAA] * 256,
        "base64",
    )
    assert len(compressed_update_data) == 2
    parsed_update_data = parse_accumulator_update(compressed_update_data[0], "base64")
    assert parsed_update_data.num_updates == 255
    assert len(parsed_update_data.updates) == 255
    parsed_update_data = parse_accumulator_update(compressed_update_data[1], "base64")
    assert parsed_update_data.num_updates == 1
    assert len(parsed_update_data.updates) == 1
