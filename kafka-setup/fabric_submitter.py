from kafka import KafkaConsumer
import json
import subprocess

# Kafka topic for AI decisions
consumer = KafkaConsumer(
    'ai-decisions',
    bootstrap_servers='localhost:9092',
    value_deserializer=lambda m: json.loads(m.decode('utf-8')),
    auto_offset_reset='earliest',
    enable_auto_commit=True
)

print("📨 Fabric Submitter is listening for AI decisions...")

for message in consumer:
    decision_data = message.value
    print(f"📥 Received decision: {decision_data}")

    # Extract values
    event_id = decision_data['event_id']
    decision = decision_data['decision']
    reason = decision_data['reason']

    # Use peer CLI to invoke the chaincode
    try:
        result = subprocess.check_output([
            'peer', 'chaincode', 'invoke',
            '-o', 'localhost:7050',
            '--ordererTLSHostnameOverride', 'orderer.example.com',
            '--tls', '--cafile', '../fabric-samples/test-network/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem',
            '-C', 'mychannel',
            '-n', 'compliance',
            '--peerAddresses', 'localhost:7051',
            '--tlsRootCertFiles', '../fabric-samples/test-network/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt',
            '-c', json.dumps({
                "function": "recordDecision",
                "Args": [event_id, decision, reason]
            })
        ])
        print(f"✅ Submitted to Fabric: {result.decode().strip()}")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error submitting to Fabric: {e.output.decode().strip()}")
