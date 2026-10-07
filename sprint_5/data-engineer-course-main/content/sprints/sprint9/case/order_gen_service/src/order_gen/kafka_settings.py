from typing import Dict, Optional, Tuple


class KafkaSetting:
    def __init__(self, host, port, username, userpass, topic, student) -> None:
        self.student = student
        self.host = host
        self.port = port
        self.username = username
        self.userpass = userpass
        self.topic = topic


class KafkaSettingParser:

    @staticmethod
    def parse_json(json: Dict) -> Tuple[Optional[KafkaSetting], Optional[str]]:
        kafka_connect_key = 'kafka_connect'
        host_key = 'host'
        port_key = 'port'
        producer_name_key = 'producer_name'
        producer_password_key = 'producer_password'
        topic_key = 'topic'
        student_key = 'student'

        if student_key not in json:
            return (None, f'No {student_key} section in json')
        student = json[student_key]

        if kafka_connect_key not in json:
            return (None, f'No {kafka_connect_key} section in json')
        kafka_connect = json[kafka_connect_key]

        if host_key not in kafka_connect:
            return (None, f'In {kafka_connect_key} section not found parameter "{host_key}"')
        host = kafka_connect[host_key]

        if port_key not in kafka_connect:
            return (None, f'In {kafka_connect_key} section not found parameter "{port_key}"')
        port = kafka_connect[port_key]

        if producer_name_key not in kafka_connect:
            return (None, f'In {kafka_connect_key} section not found parameter "{producer_name_key}"')
        producer_name = kafka_connect[producer_name_key]

        if producer_password_key not in kafka_connect:
            return (None, f'In {kafka_connect_key} section not found parameter "{producer_password_key}"')
        producer_password = kafka_connect[producer_password_key]

        if topic_key not in kafka_connect:
            return (None, f'In {kafka_connect_key} section not found parameter "{topic_key}"')
        topic = kafka_connect[topic_key]

        return (KafkaSetting(host, port, producer_name, producer_password, topic, student), None)
