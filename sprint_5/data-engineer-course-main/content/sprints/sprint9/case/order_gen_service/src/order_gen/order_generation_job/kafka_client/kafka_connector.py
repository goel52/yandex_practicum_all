import json

from confluent_kafka import Producer


def error_callback(err):
    print('Something went wrong: {}'.format(err))


class KafkaConnector:

    def __init__(self, host, port, user, password, topic, cert_path) -> None:
        params = {
            'bootstrap.servers': f'{host}:{port}',
            'security.protocol': 'SASL_SSL',
            'ssl.ca.location': cert_path,
            'sasl.mechanism': 'SCRAM-SHA-512',
            'sasl.username': user,
            'sasl.password': password,
            'error_cb': error_callback,
        }

        self.topic = topic
        self.p = Producer(params)

    def produce(self, payload):
        self.p.produce(self.topic, payload)
        self.p.flush(10)


class KafkaClient:
    def __init__(self, kafka: KafkaConnector) -> None:
        self.kafka = kafka

    def send(self, message) -> None:
        self.kafka.produce(json.dumps(message))
