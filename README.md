# 🛡️ Compliance Chaincode with Hyperledger Fabric and Kafka

This project delivers a prototype for AI-driven compliance and secure data sharing in cross-border media collaboration. It integrates **Hyperledger Fabric** for permissioned blockchain and **Apache Kafka** for scalable event streaming.

---

## 📦 Technologies Used

- Hyperledger Fabric 2.x
- Node.js chaincode
- Apache Kafka (via Docker)
- Python Kafka clients (kafka-python)
- Kafka CLI (producer/consumer)
- Docker Compose
- Fabric CA & Orderer
- CouchDB (optional)

---

## 📁 Project Structure

```
.
├── chaincode/
│   └── compliance/
│       ├── index.js
│       ├── compliance.js
│       └── package.json
├── kafka/
│   ├── docker-compose-kafka.yaml
│   ├── producer.py
│   ├── ai_compliance_checker.py
│   └── fabric_submitter.py
└── test-network/
    └── (Fabric network configs)
```

---

## 🚀 Step-by-Step Setup

---

### 1️⃣ Start Kafka

```bash
cd kafka
docker-compose -f docker-compose-kafka.yaml up -d
```

You should see:

* `zookeeper`
* `kafka-broker`
* `kafka-ui` (optional dashboard)

### 🔧 Test Kafka CLI

```bash
# Create topic
docker exec -it kafka-broker kafka-topics.sh --create --topic compliance-events --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1

# Create media-events topic
docker exec -it kafka-broker kafka-topics.sh --create --topic media-events --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1

# Create ai-decisions topic
docker exec -it kafka-broker kafka-topics.sh --create --topic ai-decisions --bootstrap-server localhost:9092 --replication-factor 1 --partitions 1

# Produce a message
docker exec -it kafka-broker kafka-console-producer.sh --broker-list localhost:9092 --topic compliance-events

# Consume message
docker exec -it kafka-broker kafka-console-consumer.sh --bootstrap-server localhost:9092 --topic compliance-events --from-beginning
```

---

### 2️⃣ Package Chaincode

```bash
peer lifecycle chaincode package compliance.tar.gz \
  --path ../chaincode/compliance \
  --lang node \
  --label compliance_1.0
```

---

### 3️⃣ Install on Both Orgs

```bash
# Org1
export CORE_PEER_LOCALMSPID="Org1MSP"
export CORE_PEER_ADDRESS=localhost:7051
export CORE_PEER_MSPCONFIGPATH=$PWD/organizations/peerOrganizations/org1.example.com/users/Admin@org1.example.com/msp
export CORE_PEER_TLS_ROOTCERT_FILE=$PWD/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt
peer lifecycle chaincode install compliance.tar.gz

# Org2
export CORE_PEER_LOCALMSPID="Org2MSP"
export CORE_PEER_ADDRESS=localhost:9051
export CORE_PEER_MSPCONFIGPATH=$PWD/organizations/peerOrganizations/org2.example.com/users/Admin@org2.example.com/msp
export CORE_PEER_TLS_ROOTCERT_FILE=$PWD/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt
peer lifecycle chaincode install compliance.tar.gz
```

---

### 4️⃣ Approve Chaincode

Use correct `PACKAGE_ID` from queryinstalled:

```bash
peer lifecycle chaincode approveformyorg \
  --channelID mychannel \
  --name compliance \
  --version 1.0 \
  --package-id compliance_1.0:<your_package_id> \
  --sequence 2 \
  --init-required \
  --tls \
  --cafile $PWD/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem \
  -o localhost:7050 \
  --ordererTLSHostnameOverride orderer.example.com
```

Repeat for both orgs.

---

### 5️⃣ Commit Chaincode

```bash
peer lifecycle chaincode commit \
  -o localhost:7050 \
  --ordererTLSHostnameOverride orderer.example.com \
  --channelID mychannel \
  --name compliance \
  --version 1.0 \
  --sequence 2 \
  --init-required \
  --tls \
  --cafile $PWD/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem \
  --peerAddresses localhost:7051 \
  --tlsRootCertFiles $PWD/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt \
  --peerAddresses localhost:9051 \
  --tlsRootCertFiles $PWD/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt
```

---

### 6️⃣ Initialize Ledger

```bash
peer chaincode invoke \
  -o localhost:7050 \
  --ordererTLSHostnameOverride orderer.example.com \
  --tls \
  --cafile $PWD/organizations/ordererOrganizations/example.com/orderers/orderer.example.com/msp/tlscacerts/tlsca.example.com-cert.pem \
  -C mychannel \
  -n compliance \
  --isInit \
  --peerAddresses localhost:7051 \
  --tlsRootCertFiles $PWD/organizations/peerOrganizations/org1.example.com/peers/peer0.org1.example.com/tls/ca.crt \
  --peerAddresses localhost:9051 \
  --tlsRootCertFiles $PWD/organizations/peerOrganizations/org2.example.com/peers/peer0.org2.example.com/tls/ca.crt \
  -c '{"function":"initLedger","Args":[]}'
```

---

## 🧠 Smart Contract Functions

### recordDecision

```bash
peer chaincode invoke \
  -C mychannel \
  -n compliance \
  -c '{"function":"recordDecision","Args":["event123", "approved", "meets all conditions"]}'
```

### queryDecision

```bash
peer chaincode query \
  -C mychannel \
  -n compliance \
  -c '{"function":"queryDecision","Args":["event123"]}'
```

### getAllDecisions

```bash
peer chaincode query \
  -C mychannel \
  -n compliance \
  -c '{"function":"getAllDecisions","Args":[]}'
```

---

## 🔄 AI Compliance Pipeline

This project includes a complete AI-driven compliance pipeline using Kafka event streaming:

### Pipeline Components

1. **producer.py** - Simulates media events with compliance metadata
2. **ai_compliance_checker.py** - AI service that processes events and makes compliance decisions
3. **fabric_submitter.py** - Submits AI decisions to Hyperledger Fabric blockchain

### Running the AI Pipeline

```bash
# Terminal 1: Start the AI compliance checker
cd kafka
python ai_compliance_checker.py

# Terminal 2: Start the Fabric submitter
python fabric_submitter.py

# Terminal 3: Send test events
python producer.py
```

### Event Flow

```
[Media Event] → Kafka → [AI Checker] → [Compliance Decision] → Kafka → [Fabric Submitter] → Blockchain
```

### Sample Event Structure

**Input (media-events topic):**
```json
{
  "event_id": "001",
  "data_type": "personal",
  "sender": "Ireland",
  "receiver": "Germany",
  "consent": true
}
```

**AI Decision (compliance-decisions topic):**
```json
{
  "event_id": "001",
  "decision": "approved",
  "reason": "Consent granted",
  "original_event": {...}
}
```

### AI Compliance Rules

The AI checker implements:
- **Consent verification** - Requires explicit consent for data transfer
- **Jurisdiction checks** - GDPR-style cross-border restrictions
- **Extensible rule engine** - Easy to add new compliance logic

---

## ✅ Smart Contract Summary

Each compliance decision stores:

```json
{
  "eventId": "event123",
  "decision": "approved",
  "reason": "meets all conditions",
  "timestamp": "2025-08-02T12:42:58.000Z",
  "docType": "decision"
}
```

---