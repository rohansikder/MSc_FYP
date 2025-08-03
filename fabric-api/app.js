const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const { getContract } = require('./gateway');

const app = express();
app.use(cors());
app.use(bodyParser.json());

app.post('/recordDecision', async (req, res) => {
    try {
        const { eventId, decision, reason } = req.body;

        const contract = await getContract();
        const result = await contract.submitTransaction('recordDecision', eventId, decision, reason || '');

        res.json({ success: true, result: JSON.parse(result.toString()) });
    } catch (error) {
        console.error('Error recording decision:', error);
        res.status(500).json({ error: error.message });
    }
});

app.get('/query/:id', async (req, res) => {
    try {
        const contract = await getContract();
        const result = await contract.evaluateTransaction('queryDecision', req.params.id);
        res.json(JSON.parse(result.toString()));
    } catch (error) {
        res.status(500).json({ error: error.message });
    }
});

const PORT = 3000;
app.listen(PORT, () => {
    console.log(`Fabric API listening on port ${PORT}`);
});
