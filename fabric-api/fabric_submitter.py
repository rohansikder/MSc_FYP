import requests
import json
from kafka import KafkaConsumer

consumer = KafkaConsumer(
    'ai-decisions',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

for message in consumer:
    decision = message.value
    payload = {
        "eventId": decision['event_id'],
        "decision": decision['decision'],
        "reason": decision['reason']
    }

    response = requests.post("http://localhost:3000/recordDecision", json=payload)
    print(f"Submitted to Fabric: {response.status_code}, {response.text}")
