import datetime
import os
import json
import requests
import argparse
import mta_utils as utils

from kafka import KafkaAdminClient, KafkaProducer
from mta_reference import MTAReference
from kafka.admin import NewTopic
from kafka.errors import TopicAlreadyExistsError


import gtfs_realtime_pb2
from google.protobuf.message import DecodeError

import logging


default_feed_url = "https://redpanda-jotb2023.ddns.net/mta_subway"


# brokers from environment
default_brokers = "localhost:9092"

REDPANDA_BROKERS_KEY = "REDPANDA_BROKERS"

if REDPANDA_BROKERS_KEY in os.environ:
    default_brokers = os.environ["REDPANDA_BROKERS"]

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-8s %(name)-15s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
log = logging.getLogger("mta-producer")


def create_topic(brokers, topic):
    admin = KafkaAdminClient(bootstrap_servers=brokers)
    try:
        admin.create_topics(
            new_topics=[
                NewTopic(
                    name=topic, num_partitions=1, replication_factor=3
                )
            ]
        )
        log.info(f"Created topic: {topic}")
    except TopicAlreadyExistsError as e:
        log.info(f"Topic already exists: {topic}")
    finally:
        admin.close()


def main():

    parser = argparse.ArgumentParser()
    parser.add_argument("--brokers", default=default_brokers)
    parser.add_argument("--topic", default="gtfs_mta_subway")
    parser.add_argument("--user", required=True)
    parser.add_argument("--ref_dir", default="ref")
    parser.add_argument("--feed-url", default=default_feed_url)

    args = parser.parse_args()

    base_dir = args.ref_dir
    ref = MTAReference(base_dir)

    # create redpanda topic
    create_topic(args.brokers, args.topic)

    # create a producer
    producer = KafkaProducer(bootstrap_servers=args.brokers, compression_type="gzip")

    def on_success(metadata):
        log.info(
            f"Sent {metadata.serialized_value_size + metadata.serialized_key_size} bytes to topic '{metadata.topic}' at offset {metadata.offset}"
        )

    def on_error(e):
        log.error(f"Error sending message: {e}")

    session = requests.Session()
    try:
        while True:
            feed = gtfs_realtime_pb2.FeedMessage()
            try:
                response = session.get(
                    default_feed_url, auth=(args.user, f"{args.user}_JOTB_2023"),timeout=(60,60)
                )
                # parse protobuf
                feed.ParseFromString(response.content)

                if not feed.header.HasField("timestamp"):
                    continue

                for entity in feed.entity:
                    message = utils.parse_vehicle_entity(entity, ref=ref)
                    if message:
                        message["feed_timestamp"] = datetime.datetime.fromtimestamp(feed.header.timestamp).strftime("%Y-%m-%d %H:%M:%S")
                        future = producer.send(
                            args.topic,
                            key=str.encode(entity.id),
                            value=json.dumps(message).encode(),
                        )
                        future.add_callback(on_success)
                        future.add_errback(on_error)
            except DecodeError:
                log.error(f"Decode error: {response.content}")
            except Exception as e:
                log.error(f"Request error: {e}")
    finally:
        producer.flush()
        producer.close()


if __name__ == "__main__":
    main()
