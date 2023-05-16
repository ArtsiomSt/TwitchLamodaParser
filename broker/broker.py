import json

from confluent_kafka import Consumer
from config import BrokerSettings
import requests


settings = BrokerSettings()

consumer = Consumer({
    'bootstrap.servers': settings.kafka_url,
    'group.id': 'my_group',
    'auto.offset.reset': 'earliest'
})

consumer.subscribe(["product", "category", "stream"])


def form_url(url):
    return settings.host+url


while True:
    msg = consumer.poll()
    if msg is None:
        continue
    if msg.error():
        print('Error while consuming message: {}'.format(msg.error()))
    else:
        topic = msg.topic()
        message_data: dict = json.loads(msg.value())
        match topic:
            case "product":
                params = {"url": message_data.get("url", None)}
                params.update(message_data.get("params", {}))
                resp = requests.post(form_url(settings.parse_product_url), params=params)
                print(resp.json(), topic)
            case "category":
                params = {"url": message_data.get("url", None)}
                params.update(message_data.get("params", {}))
                resp = requests.post(form_url(settings.parse_category_url), params=params)
                print(resp.json(), topic)
            case "stream":
                params = {}
                params.update(message_data.get("twitch_stream_params", {}))
                resp = requests.post(form_url(settings.parse_streams_url), params=params)
                print(resp.json(), topic)
        consumer.commit(message=msg)
