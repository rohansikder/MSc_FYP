import json
import time
from kafka import KafkaConsumer, KafkaProducer

# startup delay to wait for Kafka
time.sleep(5)

consumer = KafkaConsumer(
    'media-events',
    bootstrap_servers='localhost:9092',
    auto_offset_reset='earliest',
    group_id='ai-compliance-group',
    value_deserializer=lambda m: json.loads(m.decode('utf-8'))
)

producer = KafkaProducer(
    bootstrap_servers='localhost:9092',
    api_version=(0, 10),
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)


print("🧠 AI Compliance Checker is running...\n")

for msg in consumer:
    event = msg.value
    print(f"🔍 Received event: {event}")

    # Simple rule-based compliance logic
    consent = event.get("consent", False)
    sender = event.get("sender")
    receiver = event.get("receiver")

    decision = {
        "event_id": event.get("event_id"),
        "decision": "approved" if consent else "rejected",
        "reason": "Consent granted" if consent else "Missing or false consent",
        "original_event": event
    }

    # Optional jurisdiction-based rule (GDPR-style logic)
    if sender == "Germany" and receiver == "USA":
        decision["decision"] = "rejected"
        decision["reason"] = "Export to non-GDPR jurisdiction not allowed"

    print(f"✅ Compliance decision: {decision}")
    producer.send('compliance-decisions', value=decision)
