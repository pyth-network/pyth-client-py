import base64
import binascii
import struct
from struct import unpack
from typing import Any, Dict, List, Optional

from Crypto.Hash import keccak
from loguru import logger

P2W_FORMAT_MAGIC = "P2WH"
P2W_FORMAT_VER_MAJOR = 3
P2W_FORMAT_VER_MINOR = 0
P2W_FORMAT_PAYLOAD_ID = 2

DEFAULT_VAA_ENCODING = "hex"

ACCUMULATOR_MAGIC = "504e4155"

MAX_MESSAGE_IN_SINGLE_UPDATE_DATA = 255


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


class PriceUpdate:
    def __init__(self, ema_price, price_id, price):
        self.ema_price = ema_price
        self.id = price_id
        self.price = price

    def __str__(self):
        return (
            f"PriceUpdate(ema_price={self.ema_price}, id={self.id}, price={self.price})"
        )

    def to_dict(self):
        return {
            "ema_price": self.ema_price.to_dict(),
            "id": self.id,
            "price": self.price.to_dict(),
        }


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

    def to_dict(self, verbose=False, vaa_format=DEFAULT_VAA_ENCODING):
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
                "vaa": encode_vaa_for_chain(self.vaa, vaa_format),
            }
            if vaa_format
            else {}
        )

        result = {
            **self.price_feed.to_dict(),
            **metadata,
            **vaa_data,
        }

        return result


# Referenced from https://github.com/pyth-network/pyth-crosschain/blob/110caed6be3be7885773d2f6070b143cc13fb0ee/price_service/server/src/encoding.ts#L24
def encode_vaa_for_chain(vaa, vaa_format, buffer=False):
    # check if vaa is already in vaa_format
    if isinstance(vaa, str):
        if vaa_format == DEFAULT_VAA_ENCODING:
            try:
                vaa_buffer = bytes.fromhex(vaa)
            except ValueError:
                pass  # VAA is not in hex format
            else:
                # VAA is in hex format, return it as it is
                return vaa_buffer if buffer else vaa
        else:
            try:
                vaa_buffer = base64.b64decode(vaa)
            except binascii.Error:
                pass  # VAA is not in base64 format
            else:
                # VAA is in base64 format, return it as it is
                return vaa_buffer if buffer else vaa

    # Convert VAA to the specified format
    if vaa_format == DEFAULT_VAA_ENCODING:
        vaa_buffer = base64.b64decode(vaa)
        vaa_str = vaa_buffer.hex()
    else:
        vaa_buffer = bytes.fromhex(vaa)
        vaa_str = base64.b64encode(vaa_buffer).decode("ascii")

    return vaa_buffer if buffer else vaa_str


# Referenced from https://github.com/wormhole-foundation/wormhole/blob/main/sdk/js/src/vaa/wormhole.ts#L26-L56
def parse_vaa(vaa, encoding):
    vaa = encode_vaa_for_chain(vaa, encoding, buffer=True)

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


# Referenced from https://github.com/pyth-network/pyth-crosschain/blob/main/wormhole_attester/sdk/js/src/index.ts#L122
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


# Referenced from https://github.com/pyth-network/pyth-crosschain/blob/main/wormhole_attester/sdk/js/src/index.ts#L50
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


# Referenced from https://github.com/pyth-network/pyth-crosschain/blob/110caed6be3be7885773d2f6070b143cc13fb0ee/price_service/server/src/rest.ts#L139
def vaa_to_price_infos(vaa, encoding=DEFAULT_VAA_ENCODING) -> List[PriceInfo]:
    parsed_vaa = parse_vaa(vaa, encoding)
    batch_attestation = parse_batch_price_attestation(parsed_vaa["payload"])
    price_infos = []
    for price_attestation in batch_attestation["price_attestations"]:
        price_infos.append(
            create_price_info(
                price_attestation,
                vaa,
                parsed_vaa["sequence"],
                parsed_vaa["emitter_chain"],
            )
        )

    return price_infos


def vaa_to_price_info(price_feed_id, vaa, encoding=DEFAULT_VAA_ENCODING) -> PriceInfo:
    if encode_vaa_for_chain(vaa, encoding, buffer=True)[:4].hex() == ACCUMULATOR_MAGIC:
        return extract_price_info_from_accumulator_update(price_feed_id, vaa, encoding)
    price_infos = vaa_to_price_infos(vaa, encoding)
    for price_info in price_infos:
        if price_info.price_feed.id == price_feed_id:
            return price_info

    return None


# Referenced from https://github.com/pyth-network/pyth-crosschain/blob/110caed6be3be7885773d2f6070b143cc13fb0ee/price_service/server/src/listen.ts#L37
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


# Referenced from https://github.com/pyth-network/pyth-crosschain/blob/main/wormhole_attester/sdk/js/src/index.ts#L218
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

    return PriceUpdate(ema_price, price_attestation["price_id"], price)


# Referenced from https://github.com/pyth-network/pyth-crosschain/blob/1a00598334e52fc5faf967eb1170d7fc23ad828b/price_service/server/src/rest.ts#L137
def extract_price_info_from_accumulator_update(
    update_data, encoding
) -> Optional[Dict[str, Any]]:
    encoded_update_data = encode_vaa_for_chain(update_data, encoding, buffer=True)
    offset = 0
    offset += 4  # magic
    offset += 1  # major version
    offset += 1  # minor version

    trailing_header_size = encoded_update_data[offset]
    offset += 1 + trailing_header_size

    update_type = encoded_update_data[offset]
    offset += 1

    if update_type != 0:
        logger.info(f"Invalid accumulator update type: {update_type}")
        return None

    vaa_length = int.from_bytes(
        encoded_update_data[offset : offset + 2], byteorder="big"
    )
    offset += 2

    vaa_buffer = encoded_update_data[offset : offset + vaa_length]
    # convert vaa_buffer to string based on encoding
    if encoding == "hex":
        vaa_str = vaa_buffer.hex()
    elif encoding == "base64":
        vaa_str = base64.b64encode(vaa_buffer).decode("ascii")
    parsed_vaa = parse_vaa(vaa_str, encoding)
    offset += vaa_length

    num_updates = encoded_update_data[offset]
    offset += 1

    price_infos = []
    for _ in range(num_updates):
        message_length = int.from_bytes(
            encoded_update_data[offset : offset + 2], byteorder="big"
        )  # message_size: u16
        offset += 2

        message = encoded_update_data[
            offset : offset + message_length
        ]  # message: [u8; message_size]
        offset += message_length

        proof_length = encoded_update_data[offset]  # proof_size: u8
        offset += 1

        proof = []
        for _ in range(proof_length):
            hash = encoded_update_data[offset : offset + 20]
            proof.append(hash)
            offset += 20

        message_offset = 0
        message_type = message[message_offset]
        message_offset += 1

        # Message Type 0 is a price update and we ignore the rest
        if message_type != 0:
            continue

        price_id = message[message_offset : message_offset + 32].hex()
        message_offset += 32

        price = int.from_bytes(
            message[message_offset : message_offset + 8], byteorder="big", signed=True
        )
        message_offset += 8
        conf = int.from_bytes(
            message[message_offset : message_offset + 8], byteorder="big", signed=False
        )
        message_offset += 8
        expo = int.from_bytes(
            message[message_offset : message_offset + 4], byteorder="big", signed=True
        )
        message_offset += 4
        publish_time = int.from_bytes(
            message[message_offset : message_offset + 8], byteorder="big", signed=True
        )
        message_offset += 8
        prev_publish_time = int.from_bytes(
            message[message_offset : message_offset + 8], byteorder="big", signed=True
        )
        message_offset += 8
        ema_price = int.from_bytes(
            message[message_offset : message_offset + 8], byteorder="big", signed=True
        )
        message_offset += 8
        ema_conf = int.from_bytes(
            message[message_offset : message_offset + 8], byteorder="big", signed=False
        )

        price_infos.append(
            PriceInfo(
                seq_num=parsed_vaa["sequence"],
                vaa=update_data,
                publish_time=publish_time,
                attestation_time=publish_time,
                last_attested_publish_time=prev_publish_time,
                price_feed=PriceUpdate(
                    ema_price=Price(
                        price=str(ema_price),
                        conf=str(ema_conf),
                        expo=expo,
                        publish_time=publish_time,
                    ),
                    price_id=price_id,
                    price=Price(
                        price=str(price),
                        conf=str(conf),
                        expo=expo,
                        publish_time=publish_time,
                    ),
                ),
                emitter_chain_id=parsed_vaa["emitter_chain"],
            )
        )

    return price_infos


# 1. extract a list of [slot, wh_proof, price_update_message, merkle_proof] per updateData
# 2. combine the ones with the same slot to { same_slot, wh_proof, [price_update_message, merkle_proof] }
# 3. serialize it into the accumulator update format

# note: you can only merge those with the same slot
# note2: you can only merge up to 255 updates per accumulator update


# this function takes in a list of update_data and:
# - for each of the update data, check if the vaa is the same
# - if the vaa is the same, we combine them, the way we combine them is:
#   - we append the updates and increment num_updates
# - if its not the same, we dont combine it
def compress_update_data_list(update_data_list, encoding) -> List[str]:
    parsed_data_dict = {}  # use a dictionary for O(1) lookup
    # combine the ones with the same vaa to a list
    for update_data in update_data_list:
        parsed_update_data = parse_update_data(update_data, encoding)
        vaa = parsed_update_data["vaa"]

        if vaa not in parsed_data_dict:
            parsed_data_dict[vaa] = []
        parsed_data_dict[vaa].append(parsed_update_data)
    parsed_data_list = list(parsed_data_dict.values())

    # check if the number of updates in each combined_data is less than 255
    # if any of them are more than 255, we need to chunk them into size of 255 each

    # combine the ones with the same vaa to { same_vaa, num_updates, [updates1, updates2, ...] }
    combined_data_list = []
    for parsed_data in parsed_data_list:
        combined_data = {
            "magic": parsed_data[0]["magic"],
            "major_version": parsed_data[0]["major_version"],
            "minor_version": parsed_data[0]["minor_version"],
            "trailing_header_size": parsed_data[0]["trailing_header_size"],
            "update_type": parsed_data[0]["update_type"],
            "vaa_length": parsed_data[0]["vaa_length"],
            "vaa": parsed_data[0]["vaa"],
            "num_updates": sum(len(item["updates"]) for item in parsed_data),
            "updates": [update for item in parsed_data for update in item["updates"]],
        }
        combined_data_list.append(combined_data)

    # serialize it into the accumulator update format
    serialized_data_list = []
    for combined_data in combined_data_list:
        serialized_data = serialize_combined_data(combined_data)
        serialized_data_list.append(serialized_data)

    return serialized_data_list


def serialize_combined_data(combined_data):
    serialized_data = bytearray()
    serialized_data.extend(combined_data["magic"])
    serialized_data.append(combined_data["major_version"])
    serialized_data.append(combined_data["minor_version"])
    serialized_data.append(combined_data["trailing_header_size"])
    serialized_data.append(combined_data["update_type"])
    serialized_data.extend(combined_data["vaa_length"].to_bytes(2, byteorder="big"))
    serialized_data.extend(combined_data["vaa"])
    serialized_data.append(combined_data["num_updates"])
    for update in combined_data["updates"]:
        serialized_data.extend(update["message_size"].to_bytes(2, byteorder="big"))
        serialized_data.extend(update["message"])
        serialized_data.append(update["proof_size"])
        for proof in update["proof"]:
            serialized_data.extend(proof)
    return serialized_data.hex()


def parse_update_data(update_data, encoding):
    encoded_update_data = encode_vaa_for_chain(update_data, encoding, buffer=True)
    offset = 0
    magic = encoded_update_data[offset : offset + 4]
    offset += 4
    major_version = encoded_update_data[offset]
    offset += 1
    minor_version = encoded_update_data[offset]
    offset += 1

    trailing_header_size = encoded_update_data[offset]
    offset += 1 + trailing_header_size

    update_type = encoded_update_data[offset]
    offset += 1

    if update_type != 0:
        logger.info(f"Invalid accumulator update type: {update_type}")
        return None

    vaa_length = int.from_bytes(
        encoded_update_data[offset : offset + 2], byteorder="big"
    )
    offset += 2

    vaa_buffer = encoded_update_data[offset : offset + vaa_length]
    offset += vaa_length

    num_updates = encoded_update_data[offset]
    offset += 1

    updates = []
    for _ in range(num_updates):
        message_size = int.from_bytes(
            encoded_update_data[offset : offset + 2], byteorder="big"
        )
        offset += 2

        message = encoded_update_data[offset : offset + message_size]
        offset += message_size

        proof_size = encoded_update_data[offset]
        offset += 1

        proof = []
        for _ in range(proof_size):
            hash = encoded_update_data[offset : offset + 20]
            proof.append(hash)
            offset += 20

        updates.append(
            {
                "message_size": message_size,
                "message": message,
                "proof_size": proof_size,
                "proof": proof,
            }
        )
    return {
        "magic": magic,
        "major_version": major_version,
        "minor_version": minor_version,
        "trailing_header_size": trailing_header_size,
        "update_type": update_type,
        "vaa_length": vaa_length,
        "vaa": vaa_buffer,
        "num_updates": num_updates,
        "updates": updates,
    }
