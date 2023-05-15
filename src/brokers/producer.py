from confluent_kafka import Producer

producer = Producer({'bootstrap.servers': 'kafka:29092'})
