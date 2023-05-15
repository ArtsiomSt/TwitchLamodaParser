from confluent_kafka import Consumer, KafkaError


# create a Kafka consumer
consumer = Consumer({
    'bootstrap.servers': 'kafka:29092',
    'group.id': 'my_group',
    'auto.offset.reset': 'earliest'
})

# subscribe to the topic
consumer.subscribe(['my_topic', "product"])

# consume messages
while True:
    msg = consumer.poll(1.0)

    if msg is None:
        continue

    if msg.error():
        if msg.error().code() == KafkaError._PARTITION_EOF:
            print('Reached end of partition')
        else:
            print('Error while consuming message: {}'.format(msg.error()))
    else:
        print('Received message: key={}, value={}'.format(msg.key(), msg.value()))
