import json
import time
from kafka import KafkaProducer

# Give Kafka time to finish startup
time.sleep(10)

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    api_version=(0, 10),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

event = {
    "event_id": "001",
    "data_type": "personal",
    "sender": "Ireland",
    "receiver": "Germany",
    "consent": True
}

producer.send('media-events', value=event)
print("✅ Event sent to Kafka:", event)
