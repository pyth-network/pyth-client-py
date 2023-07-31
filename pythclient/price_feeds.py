import json
import logging
from struct import unpack

from Crypto.Hash import keccak

P2W_FORMAT_MAGIC = "P2WH"
P2W_FORMAT_VER_MAJOR = 3
P2W_FORMAT_VER_MINOR = 0
P2W_FORMAT_PAYLOAD_ID = 2

DEFAULT_VAA_ENCODING = "base64"
CHAIN_TO_ENCODING = {
    "evm": "0x",
    "cosmos": "base64",
    "aptos": "base64",
    "default": "base64",
}


class Price:
    def __init__(self, conf, expo, price, publish_time):
        self.conf = conf
        self.expo = expo
        self.price = price
        self.publish_time = publish_time

    def __str__(self):
        return f"Price(conf={self.conf}, expo={self.expo}, price={self.price}, publish_time={self.publish_time})"

    def to_dict(self):
        return {
            "conf": self.conf,
            "expo": self.expo,
            "price": self.price,
            "publish_time": self.publish_time,
        }

    def to_json(self):
        return json.dumps(
            {
                "conf": self.conf,
                "expo": self.expo,
                "price": self.price,
                "publish_time": self.publish_time,
            }
        )


class PriceFeed:
    def __init__(self, ema_price, price_id, price):
        self.ema_price = ema_price
        self.id = price_id
        self.price = price

    def __str__(self):
        return (
            f"PriceFeed(ema_price={self.ema_price}, id={self.id}, price={self.price})"
        )

    def to_dict(self):
        return {
            "ema_price": self.ema_price.to_dict(),
            "id": self.id,
            "price": self.price.to_dict(),
        }

    def to_json(self):
        return json.dumps(
            {
                "ema_price": self.ema_price.to_dict(),
                "id": self.id,
                "price": self.price.to_dict(),
            }
        )


class PriceInfo:
    def __init__(
        self,
        seq_num,
        vaa,
        publish_time,
        attestation_time,
        last_attested_publish_time,
        price_feed,
        emitter_chain_id,
    ):
        self.seq_num = seq_num
        self.vaa = vaa
        self.publish_time = publish_time
        self.attestation_time = attestation_time
        self.last_attested_publish_time = last_attested_publish_time
        self.price_feed = price_feed
        self.emitter_chain_id = emitter_chain_id

    def __str__(self):
        return (
            f"SeqNum: {self.seq_num}\n"
            f"VAA: {self.vaa}\n"
            f"Publish Time: {self.publish_time}\n"
            f"Attestation Time: {self.attestation_time}\n"
            f"Last Attested Publish Time: {self.last_attested_publish_time}\n"
            f"Price Feed: {self.price_feed}\n"
            f"Emitter Chain ID: {self.emitter_chain_id}\n"
        )

    def to_dict(self):
        return {
            "seq_num": self.seq_num,
            "vaa": self.vaa,
            "publish_time": self.publish_time,
            "attestation_time": self.attestation_time,
            "last_attested_publish_time": self.last_attested_publish_time,
            "price_feed": self.price_feed.to_dict(),
            "emitter_chain_id": self.emitter_chain_id,
        }

    def to_json(self, verbose=False, target_chain=None):
        metadata = (
            {
                "emitter_chain": self.emitter_chain_id,
                "attestation_time": self.attestation_time,
                "sequence_number": self.seq_num,
            }
            if verbose
            else {}
        )

        vaa_data = (
            {
                "vaa": encode_vaa_for_chain(self.vaa, target_chain),
            }
            if target_chain
            else {}
        )

        result = {
            **self.price_feed.to_dict(),
            **metadata,
            **vaa_data,
        }

        return json.dumps(result)


def encode_vaa_for_chain(vaa, target_chain):
    encoding = CHAIN_TO_ENCODING[target_chain]

    if isinstance(vaa, str):
        if encoding == DEFAULT_VAA_ENCODING:
            return vaa
        else:
            vaa_buffer = (
                bytes.fromhex(vaa)
                if vaa.startswith("0x")
                else bytes(vaa, encoding=DEFAULT_VAA_ENCODING)
            )
    else:
        vaa_buffer = bytes(vaa)

    if encoding == "0x":
        return "0x" + vaa_buffer.hex()
    else:
        return vaa_buffer.decode(encoding)


def parse_vaa(vaa):
    if isinstance(vaa, str):
        vaa = bytes.fromhex(vaa)

    num_signers = vaa[5]
    sig_length = 66
    sig_start = 6
    guardian_signatures = []

    for i in range(num_signers):
        start = sig_start + i * sig_length
        index = vaa[start]
        signature = vaa[start + 1 : start + 66]
        guardian_signatures.append({"index": index, "signature": signature})

    body = vaa[sig_start + sig_length * num_signers :]
    version = vaa[0]
    guardian_set_index = unpack(">I", vaa[1:5])[0]
    timestamp = unpack(">I", body[0:4])[0]
    nonce = unpack(">I", body[4:8])[0]
    emitter_chain = unpack(">H", body[8:10])[0]
    emitter_address = body[10:42]
    sequence = int.from_bytes(body[42:50], byteorder="big")
    consistency_level = body[50]
    payload = body[51:]

    # Compute the hash using pycryptodome's keccak
    keccak_hash = keccak.new(digest_bits=256)
    keccak_hash.update(body)
    hash_val = keccak_hash.hexdigest()

    return {
        "version": version,
        "guardian_set_index": guardian_set_index,
        "guardian_signatures": guardian_signatures,
        "timestamp": timestamp,
        "nonce": nonce,
        "emitter_chain": emitter_chain,
        "emitter_address": emitter_address,
        "sequence": sequence,
        "consistency_level": consistency_level,
        "payload": payload,
        "hash": hash_val,
    }


def parse_batch_price_attestation(bytes_):
    offset = 0

    magic = bytes_[offset : offset + 4].decode("utf-8")
    offset += 4
    if magic != P2W_FORMAT_MAGIC:
        raise ValueError(f"Invalid magic: {magic}, expected: {P2W_FORMAT_MAGIC}")

    version_major = int.from_bytes(bytes_[offset : offset + 2], byteorder="big")
    offset += 2
    if version_major != P2W_FORMAT_VER_MAJOR:
        raise ValueError(
            f"Unsupported major version: {version_major}, expected: {P2W_FORMAT_VER_MAJOR}"
        )

    version_minor = int.from_bytes(bytes_[offset : offset + 2], byteorder="big")
    offset += 2
    if version_minor < P2W_FORMAT_VER_MINOR:
        raise ValueError(
            f"Unsupported minor version: {version_minor}, expected: {P2W_FORMAT_VER_MINOR}"
        )

    header_size = int.from_bytes(bytes_[offset : offset + 2], byteorder="big")
    offset += 2
    header_offset = 0

    payload_id = int.from_bytes(
        bytes_[offset + header_offset : offset + header_offset + 1], byteorder="big"
    )
    header_offset += 1
    if payload_id != P2W_FORMAT_PAYLOAD_ID:
        raise ValueError(
            f"Invalid payload_id: {payload_id}, expected: {P2W_FORMAT_PAYLOAD_ID}"
        )

    offset += header_size
    batch_len = int.from_bytes(bytes_[offset : offset + 2], byteorder="big")
    offset += 2
    attestation_size = int.from_bytes(bytes_[offset : offset + 2], byteorder="big")
    offset += 2

    price_attestations = []
    for i in range(batch_len):
        price_attestations.append(
            parse_price_attestation(bytes_[offset : offset + attestation_size])
        )
        offset += attestation_size

    if offset != len(bytes_):
        raise ValueError(f"Invalid length: {len(bytes_)}, expected: {offset}")

    return {
        "price_attestations": price_attestations,
    }


def parse_price_attestation(bytes_):
    offset = 0

    product_id = bytes_[offset : offset + 32].hex()
    offset += 32

    price_id = bytes_[offset : offset + 32].hex()
    offset += 32

    price = int.from_bytes(bytes_[offset : offset + 8], byteorder="big", signed=True)
    offset += 8

    conf = int.from_bytes(bytes_[offset : offset + 8], byteorder="big", signed=False)
    offset += 8

    expo = int.from_bytes(bytes_[offset : offset + 4], byteorder="big", signed=True)
    offset += 4

    ema_price = int.from_bytes(
        bytes_[offset : offset + 8], byteorder="big", signed=True
    )
    offset += 8

    ema_conf = int.from_bytes(
        bytes_[offset : offset + 8], byteorder="big", signed=False
    )
    offset += 8

    status = int.from_bytes(bytes_[offset : offset + 1], byteorder="big")
    offset += 1

    num_publishers = int.from_bytes(
        bytes_[offset : offset + 4], byteorder="big", signed=False
    )
    offset += 4

    max_num_publishers = int.from_bytes(
        bytes_[offset : offset + 4], byteorder="big", signed=False
    )
    offset += 4

    attestation_time = int.from_bytes(
        bytes_[offset : offset + 8], byteorder="big", signed=True
    )
    offset += 8

    publish_time = int.from_bytes(
        bytes_[offset : offset + 8], byteorder="big", signed=True
    )
    offset += 8

    prev_publish_time = int.from_bytes(
        bytes_[offset : offset + 8], byteorder="big", signed=True
    )
    offset += 8

    prev_price = int.from_bytes(
        bytes_[offset : offset + 8], byteorder="big", signed=True
    )
    offset += 8

    prev_conf = int.from_bytes(
        bytes_[offset : offset + 8], byteorder="big", signed=False
    )
    offset += 8

    last_attested_publish_time = int.from_bytes(
        bytes_[offset : offset + 8], byteorder="big", signed=True
    )
    offset += 8

    return {
        "product_id": product_id,
        "price_id": price_id,
        "price": str(price),
        "conf": str(conf),
        "expo": expo,
        "ema_price": str(ema_price),
        "ema_conf": str(ema_conf),
        "status": status,
        "num_publishers": num_publishers,
        "max_num_publishers": max_num_publishers,
        "attestation_time": attestation_time,
        "publish_time": publish_time,
        "prev_publish_time": prev_publish_time,
        "prev_price": str(prev_price),
        "prev_conf": str(prev_conf),
        "last_attested_publish_time": last_attested_publish_time,
    }


def vaa_to_price_info(price_feed_id, vaa) -> PriceInfo:
    parsed_vaa = parse_vaa(vaa)

    try:
        batch_attestation = parse_batch_price_attestation(parsed_vaa["payload"])
    except Exception as e:
        logging.error(e)
        logging.error(f"Parsing historical VAA failed: {parsed_vaa}")
        return None

    for price_attestation in batch_attestation["price_attestations"]:
        if price_attestation["price_id"] == price_feed_id:
            return create_price_info(
                price_attestation,
                vaa,
                parsed_vaa["sequence"],
                parsed_vaa["emitter_chain"],
            )

    return None


def create_price_info(price_attestation, vaa, sequence, emitter_chain):
    price_feed = price_attestation_to_price_feed(price_attestation)
    return PriceInfo(
        seq_num=int(sequence),
        vaa=vaa,
        publish_time=price_attestation["publish_time"],
        attestation_time=price_attestation["attestation_time"],
        last_attested_publish_time=price_attestation["last_attested_publish_time"],
        price_feed=price_feed,
        emitter_chain_id=emitter_chain,
    )


def price_attestation_to_price_feed(price_attestation):
    ema_price = Price(
        price_attestation["ema_conf"],
        price_attestation["expo"],
        price_attestation["ema_price"],
        price_attestation["publish_time"],
    )

    if price_attestation["status"] == 1:  # Assuming 1 means Trading
        price = Price(
            price_attestation["conf"],
            price_attestation["expo"],
            price_attestation["price"],
            price_attestation["publish_time"],
        )
    else:
        price = Price(
            price_attestation["prev_conf"],
            price_attestation["expo"],
            price_attestation["prev_price"],
            price_attestation["prev_publish_time"],
        )
        ema_price.publish_time = price_attestation["prev_publish_time"]

    return PriceFeed(ema_price, price_attestation["price_id"], price)


id = "e62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43"
vaa = "01000000030d00ca037dde1419ea373de7474bff80268e41f55e84dd8e4fa5e5167808111e63e4064efcfd93075d9d162090bc478a017603ef56c4d26e0c46e0af6128c08984470002e9abd7c4e62bbc6b453c5ca014b7313bbadb17d6443190d6679b7c0ccb03bae619d21dcb5d6d5a484f9e4fd5586dca7c20403dc80d61dbe682a436b4d15d10bc0003a5e748513b75e34d9db61c6fd0fa55533e8424d88fbe6cda8e7cf61d50cb9467192a5cbd47b14b205b38123ad4b7c39d6ce7d6bf02c4a1452d135dc29fc83ef600049e4cd56e3c2e0cfc4cc831bc4ec54410590c15b4b20b63cc91be3436a4d09c0c22be4ab96962ad6e94d83e14c770e122aebae6fdbdea97f98cec7da5d30ed2a40106a7565c6387a700e02ee09652b40bdeef044441ca1e3b3c9376d4a129d22ca861501c3f5c0e8469c9a0e5d1b09d9f84c6517c0a2b400c0b47552006fff1dad3a5000a4db87004c483f899b5fd766c14334dfb5ca2fa5698964cf9644669b325bd3485207cbc4180a360023d1412da68bb11a0a82fee70a6bf03dda30b7aae53e0e465010ba3a6e45c9d8ef1d1041fdc7a926a9f41075531d45824144bbc720d111ee7270a77dd6dd65558b30d0f03692e075bd7d96cdfb24f5a68fecc22e441ded230c9cc010c09380e394e2b30fd036f13152b115dab7a206270d52255dfbbf0505c67bf510e70d0a6075f9bae19235eaf8a0893a4af9ed0df1b8cd67e1fe7b2ec61178d3ca4010dc491600d07d10a6468fb5955d94bc114efab46104e2ae530931231fea52cf7e32964a1c8bfe0ee38aaa8abfe8edcb7c079b6dd97b2c317c9d71cb5973bb53c72010f787e3c59ac484fdca7d5e41b29cebee08cb1789d61a0f29ccd0353118fd667ab1473a626eb6c237cff70ffb1eb2a556862197b08f183d5852168f5ce0f92632b0110f7ee4abdedc936ebebe86b3493292a9fa6625ab910b4a1340b46478a819508d1261f3d559d5cc95dead635c215b80b1cb2df348639d1ca572d3d14f07dc38908011103e3cdc9936ffbb7c0af5d77a4c092c5c42de161c9254919d19af718defd71a757fcbb1e3772e72c3a8c8291ab36f628a060030abf8ffb43923bb1a05cf9605d0112ddea2ce8ec77b9e222db5f1a95861c3da2ed3f54f7e937008bcc14b2458b98990eeb5910c7e9b2a27ff47a9568d0a3fedc12f357323905cbc8a1be6acbc5986b0064c37bca00000000001af8cd23c2ab91237730770bbea08d61005cdda0984348f3f6eecb559638c0bba0000000002144b1420150325748000300010001020005009d2efa1235ab86c0935cb424b102be4f217e74d1109df9e75dfa8338fc0f0908782f95862b045670cd22bee3114c39763a4a08beeb663b145d283c31d7d1101c4f000000059cc51c400000000000e4e1bffffffff8000000059b3f3c700000000000eae895010000001a0000001e0000000064c37bca0000000064c37bca0000000064c37bc9000000059cc51c400000000000e4e1bf0000000064c37bc948d6033d733e27950c2e0351e2505491cd9154824f716d9513514c74b9f98f583dd2b63686a450ec7290df3a1e0b583c0481f651351edfa7636f39aed55cf8a300000005a7462c060000000000d206a2fffffff800000005a5c499380000000000f44b7d010000001c000000200000000064c37bca0000000064c37bca0000000064c37bc900000005a74653cc0000000000d1dedc0000000064c37bc83515b3861e8fe93e5f540ba4077c216404782b86d5e78077b3cbfd27313ab3bce62df6c8b4a85fe1a67db44dc12de5db330f7ac66b72dc658afedf0f4a415b43000002a724c9d1000000000032396fc5fffffff8000002a6e3e0fec0000000002ee4815c010000001b000000200000000064c37bca0000000064c37bca0000000064c37bc9000002a724c9d1000000000032396fc50000000064c37bc99b5f73e0075e7d70376012180ddba94272f68d85eae4104e335561c982253d41a19d04ac696c7a6616d291c7e5d1377cc8be437c327b75adb5dc1bad745fcae800000000045152eb000000000001bb63fffffff800000000044de0b500000000000185df0100000015000000160000000064c37bca0000000064c37bca0000000064c37bc900000000045152eb000000000001bb630000000064c37bc8e876fcd130add8984a33aab52af36bc1b9f822c9ebe376f3aa72d630974e15f0dcef50dd0a4cd2dcc17e45df1676dcb336a11a61c69df7a0299b0150c672d25c000000000074990500000000000011d9fffffff80000000000748c2f000000000000116f010000001b000000200000000064c37bca0000000064c37bca0000000064c37bc900000000007498d400000000000011a80000000064c37bc9"
price_info = vaa_to_price_info(id, vaa)

print(price_info.to_json())
