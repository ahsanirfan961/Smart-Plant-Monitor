/*
Smart Plant IoT - Express.js Backend API Server
Connects MQTT and WebSocket for real-time dashboard
*/

const express = require('express');
const http = require('http');
const socketIO = require('socket.io');
const path = require('path');
const mqtt = require('mqtt');
const admin = require('firebase-admin');
require('dotenv').config();

// Initialize Firebase Admin SDK (for server-side use)
let database = null;
let firebaseEnabled = false;

try {
  // Use environment variable or direct URL
  const databaseURL = process.env.FIREBASE_DATABASE_URL || 
    "https://smart-plant-monitor-bae74-default-rtdb.firebaseio.com";
  
  // Check if already initialized
  if (!admin.apps.length) {
    admin.initializeApp({
      databaseURL: databaseURL
    });
  }
  
  database = admin.database();
  firebaseEnabled = true;
  console.log('[Firebase] Admin SDK initialized successfully');
} catch (error) {
  console.warn('[Firebase] Initialization error:', error.message);
  firebaseEnabled = false;
}

// Configuration
const PORT = 3003;
// For local development: use 192.168.240.1 (Docker bridge network)
// For Docker deployment: use 'mqtt://mosquitto:1883' (container DNS)
const MQTT_BROKER = process.env.MQTT_BROKER || 'mqtt://192.168.240.1:1883';

console.log(`[Config] MQTT Broker: ${MQTT_BROKER}`);
console.log(`[Config] Port: ${PORT}`);

// Track last stored values to avoid duplicate writes to Firebase
const lastStoredValues = {
    sensors: null,
    actuators: null,
    predictions: null
};

// Rate limiting - process at most 1 message per second
let lastProcessedTime = 0;
const RATE_LIMIT_MS = 3000; // 1 second between messages

// Initialize Express and Socket.IO
const app = express();
const server = http.createServer(app);
const io = socketIO(server, {
    cors: {
        origin: "*",
        methods: ["GET", "POST"]
    }
});

// Middleware
app.use(express.json());
app.use(express.static(path.join(__dirname, '../frontend')));

// Global state
const systemState = {
    sensors: {
        temperature: 0,
        humidity: 0,
        soil_moisture: 0,
        light_intensity: 0,
        timestamp: null
    },
    actuators: {
        pump: 'OFF',
        fan: 'OFF',
        grow_light: 'OFF',
        timestamp: null
    },
    predictions: {
        dryness: {},
        health: {}
    },
    history: {
        sensors: []
    }
};

// MQTT Client Setup
let mqttClient = null;

function connectMQTT() {
    console.log('Connecting to MQTT broker:', MQTT_BROKER);
    
    mqttClient = mqtt.connect(MQTT_BROKER, {
        clientId: 'smart-plant-dashboard-' + Date.now(),
        clean: true,  // Clean session - don't restore subscriptions
        cleanSession: true,
        reconnectPeriod: 1000
    });

    mqttClient.on('connect', () => {
        console.log('Connected to MQTT broker');
        
        // Subscribe to all topics
        mqttClient.subscribe([
            'plant-iot/sensors/aggregated',
            'plant-iot/status/all',
            'plant-iot/status/pump',
            'plant-iot/status/fan',
            'plant-iot/status/grow-light',
            'plant-iot/predictions/soil-dryness',
            'plant-iot/predictions/health-score',
            'plant-iot/analytics/anomalies',
            'plant-iot/events/alerts'
        ], (err) => {
            if (err) {
                console.error('Subscribe error:', err);
            } else {
                console.log('Subscribed to MQTT topics');
            }
        });
    });

    mqttClient.on('message', (topic, message) => {
        try {
            // Rate limiting - skip if we've processed a message too recently
            const now = Date.now();
            if (now - lastProcessedTime < RATE_LIMIT_MS) {
                return; // Skip this message, it's too soon
            }
            lastProcessedTime = now;
            
            let payload;
            try {
                payload = JSON.parse(message.toString());
            } catch (parseError) {
                console.error(`JSON parse error on topic ${topic}:`, message.toString());
                return; // Skip this message
            }
            
            console.log(`[${new Date().toLocaleTimeString()}] MQTT: ${topic}`, payload);
            console.log(`[SOCKET.IO] Broadcasting to ${io.engine.clientsCount} connected clients`);
            
            // Route message handling
            if (topic === 'plant-iot/sensors/aggregated') {
                // Normalize sensor data - extract percent values
                const normalizedSensors = {
                    timestamp: payload.timestamp,
                    temperature: payload.temperature,
                    humidity: payload.humidity,
                    soil_moisture: payload.soil_moisture_percent !== undefined ? payload.soil_moisture_percent : payload.soil_moisture,
                    light_intensity: payload.light_percent !== undefined ? payload.light_percent : payload.light_intensity,
                    quality: payload.quality
                };
                
                systemState.sensors = normalizedSensors;
                
                // Store to Firebase (with deduplication)
                storeSensorData(normalizedSensors);
                
                // Add to history
                if (systemState.history.sensors.length >= 288) { // 24 hours * 12 (5-min intervals)
                    systemState.history.sensors.shift();
                }
                systemState.history.sensors.push(normalizedSensors);
                
                // Broadcast to all connected clients
                io.emit('sensor-data', normalizedSensors);
                io.emit('sensor-update', normalizedSensors);
                
            } else if (topic === 'plant-iot/status/all') {
                systemState.actuators = payload;
                
                // Store to Firebase (with deduplication)
                storeActuatorStatus(payload);
                
                io.emit('actuator-status', payload);
                
            } else if (topic.includes('predictions')) {
                if (topic.includes('soil-dryness')) {
                    systemState.predictions.dryness = payload;
                } else if (topic.includes('health-score')) {
                    systemState.predictions.health = payload;
                }
                
                // Store to Firebase (with deduplication)
                storePredictions(systemState.predictions);
                
                io.emit('predictions', systemState.predictions);
                
            } else if (topic.includes('anomalies') || topic.includes('alerts')) {
                // Only broadcast anomalies if there are actual anomalies
                if (payload.anomalies && payload.anomalies.length > 0) {
                    io.emit('alert', {
                        type: 'warning',
                        message: `Anomaly detected: ${JSON.stringify(payload.anomalies[0])}`
                    });
                    console.log(`[ANOMALY] ${JSON.stringify(payload.anomalies)}`);
                }
            }
            
        } catch (error) {
            console.error('Error processing MQTT message:', error);
        }
    });

    mqttClient.on('error', (error) => {
        console.error('MQTT error:', error);
    });

    mqttClient.on('offline', () => {
        console.log('MQTT client offline');
    });

    mqttClient.on('reconnect', () => {
        console.log('MQTT client reconnecting...');
    });
}

// Connect to MQTT
connectMQTT();

/* ========== Firebase Validation Functions ========== */

// Create a combined sensor string for deduplication
function createSensorString(sensorData) {
    return `T:${Math.round(sensorData.temperature)}H:${Math.round(sensorData.humidity)}M:${sensorData.soil_moisture}L:${sensorData.light_intensity}`;
}

// Check if sensor data already exists in Firestore
async function checkSensorInFirebase(sensorData) {
    if (!firebaseEnabled || !database) return false;
    
    try {
        const currentSensorString = createSensorString(sensorData);
        
        // Get the last stored sensor record
        const snapshot = await database.ref('sensors').orderByChild('storedAt').limitToLast(1).once('value');
        
        if (snapshot.exists()) {
            const lastRecord = Object.values(snapshot.val())[0];
            const lastSensorString = createSensorString(lastRecord);
            
            if (currentSensorString === lastSensorString) {
                console.log(`[Firebase] Sensor duplicate detected: ${currentSensorString} - skipping storage`);
                return true; // Data exists, skip storage
            }
        }
        
        return false; // Data is new, proceed with storage
    } catch (error) {
        console.error('[Firebase] Error checking sensor data:', error.message);
        return false; // On error, allow storage
    }
}

// Check if actuator status already exists in Firestore
async function checkActuatorInFirebase(actuatorData) {
    if (!firebaseEnabled || !database) return false;
    
    try {
        const currentActuatorString = JSON.stringify(actuatorData);
        
        // Get the last stored actuator record
        const snapshot = await database.ref('actuators/history').orderByChild('storedAt').limitToLast(1).once('value');
        
        if (snapshot.exists()) {
            const lastRecord = Object.values(snapshot.val())[0];
            const lastActuatorString = JSON.stringify({ pump: lastRecord.pump, fan: lastRecord.fan, grow_light: lastRecord.grow_light });
            
            if (currentActuatorString === lastActuatorString) {
                console.log(`[Firebase] Actuator duplicate detected - skipping storage`);
                return true; // Data exists, skip storage
            }
        }
        
        return false; // Data is new, proceed with storage
    } catch (error) {
        console.error('[Firebase] Error checking actuator data:', error.message);
        return false; // On error, allow storage
    }
}

/* ========== Firebase Storage Functions ========== */

// Check if data has changed significantly (to avoid duplicates)
function hasDataChanged(category, newData) {
    const lastData = lastStoredValues[category];
    if (!lastData) return true; // Always store if no previous data
    
    // For sensors, check if any value differs
    if (category === 'sensors') {
        return JSON.stringify(newData) !== JSON.stringify(lastData);
    }
    
    // For actuators, check if status changed
    if (category === 'actuators') {
        return JSON.stringify(newData) !== JSON.stringify(lastData);
    }
    
    // For predictions, check if values differ
    if (category === 'predictions') {
        return JSON.stringify(newData) !== JSON.stringify(lastData);
    }
    
    return true;
}

// Store sensor data to Firebase
async function storeSensorData(sensorData) {
    if (!firebaseEnabled || !database) return;
    
    try {
        // First check in-memory cache
        if (!hasDataChanged('sensors', sensorData)) {
            console.log('[Firebase] Duplicate sensor data (cache) - skipping storage');
            return;
        }
        
        // Then check Firestore database for validation
        const existsInFirebase = await checkSensorInFirebase(sensorData);
        if (existsInFirebase) {
            return; // Data already in Firestore, skip
        }
        
        const timestamp = new Date().toISOString();
        const dataToStore = {
            ...sensorData,
            sensorString: createSensorString(sensorData),  // Store the combined string for easy lookup
            storedAt: timestamp
        };
        
        // Push to sensors history
        await database.ref('sensors').push(dataToStore);
        
        // Update current sensor data
        await database.ref('current/sensors').set(dataToStore);
        
        lastStoredValues.sensors = sensorData;
        console.log('[Firebase] Sensor data stored (new record)');
    } catch (error) {
        console.error('[Firebase] Error storing sensor data:', error.message);
    }
}

// Store actuator status to Firebase
async function storeActuatorStatus(actuatorData) {
    if (!firebaseEnabled || !database) return;
    
    try {
        // First check in-memory cache
        if (!hasDataChanged('actuators', actuatorData)) {
            console.log('[Firebase] Duplicate actuator data (cache) - skipping storage');
            return;
        }
        
        // Then check Firestore database for validation
        const existsInFirebase = await checkActuatorInFirebase(actuatorData);
        if (existsInFirebase) {
            return; // Data already in Firestore, skip
        }
        
        const timestamp = new Date().toISOString();
        const dataToStore = {
            ...actuatorData,
            storedAt: timestamp
        };
        
        // Push to actuators history
        await database.ref('actuators/history').push(dataToStore);
        
        // Update current actuator status
        await database.ref('current/actuators').set(dataToStore);
        
        lastStoredValues.actuators = actuatorData;
        console.log('[Firebase] Actuator status stored (new record)');
    } catch (error) {
        console.error('[Firebase] Error storing actuator status:', error.message);
    }
}

// Store predictions to Firebase
async function storePredictions(predictionData) {
    if (!firebaseEnabled || !database) return;
    
    try {
        if (!hasDataChanged('predictions', predictionData)) {
            console.log('[Firebase] Duplicate prediction data - skipping storage');
            return;
        }
        
        const timestamp = new Date().toISOString();
        const dataToStore = {
            ...predictionData,
            storedAt: timestamp
        };
        
        // Push to predictions history
        await database.ref('predictions/history').push(dataToStore);
        
        // Update current predictions
        await database.ref('current/predictions').set(dataToStore);
        
        lastStoredValues.predictions = predictionData;
        console.log('[Firebase] Predictions stored');
    } catch (error) {
        console.error('[Firebase] Error storing predictions:', error.message);
    }
}

/* ========== REST API Endpoints ========= */

// Get current data
app.get('/api/data', (req, res) => {
    res.json({
        sensors: systemState.sensors,
        actuators: systemState.actuators,
        timestamp: new Date().toISOString()
    });
});

// Get predictions
app.get('/api/predictions', (req, res) => {
    res.json(systemState.predictions);
});

// Get historical data
app.get('/api/history', (req, res) => {
    const hours = parseInt(req.query.hours) || 24;
    const limit = hours * 12; // 5-minute intervals
    
    const history = systemState.history.sensors.slice(-limit);
    res.json(history);
});

// Send command to actuator
app.post('/api/command/:actuator', (req, res) => {
    const { actuator } = req.params;
    const { action, duration } = req.body;

    if (!['pump', 'fan', 'grow_light'].includes(actuator)) {
        return res.status(400).json({ error: 'Invalid actuator' });
    }

    if (!['ON', 'OFF'].includes(action)) {
        return res.status(400).json({ error: 'Invalid action' });
    }

    // Map front-end name to MQTT topic
    const topicMap = {
        'pump': 'plant-iot/actuators/pump',
        'fan': 'plant-iot/actuators/fan',
        'grow_light': 'plant-iot/actuators/grow-light'
    };

    const topic = topicMap[actuator];
    const payload = JSON.stringify({
        action: action,
        duration: duration || 0,
        timestamp: Date.now()
    });

    if (mqttClient && mqttClient.connected) {
        mqttClient.publish(topic, payload, { qos: 1 }, (err) => {
            if (err) {
                console.error('Publish error:', err);
                res.status(500).json({ error: 'Failed to send command' });
            } else {
                console.log(`Command sent: ${actuator} -> ${action}`);
                res.json({
                    success: true,
                    actuator: actuator,
                    action: action
                });
            }
        });
    } else {
        res.status(503).json({ error: 'MQTT not connected' });
    }
});

// Get system status
app.get('/api/status', (req, res) => {
    res.json({
        mqtt_connected: mqttClient && mqttClient.connected,
        websocket_connected: io.engine.clientsCount,
        system_state: systemState,
        uptime: process.uptime()
    });
});

// Serve dashboard
app.get('/', (req, res) => {
    res.sendFile(path.join(__dirname, '../frontend/index.html'));
});

/* ========== Socket.IO Events ========== */

io.on('connection', (socket) => {
    console.log('New client connected:', socket.id);

    // Send current state to new client
    socket.emit('sensor-data', systemState.sensors);
    socket.emit('actuator-status', systemState.actuators);
    socket.emit('predictions', systemState.predictions);

    socket.on('request-data', () => {
        socket.emit('sensor-data', systemState.sensors);
        socket.emit('actuator-status', systemState.actuators);
        socket.emit('predictions', systemState.predictions);
    });

    socket.on('disconnect', () => {
        console.log('Client disconnected:', socket.id);
    });

    socket.on('error', (error) => {
        console.error('Socket error:', error);
    });
});

/* ========== Start Server ========== */

server.listen(PORT, () => {
    console.log(`
    ╔═════════════════════════════════════════╗
    ║   Smart Plant IoT Dashboard Server      ║
    ║   Running on http://localhost:${PORT}    ║
    ║   ${new Date().toLocaleString()}  ║
    ╚═════════════════════════════════════════╝
    `);
});

// Graceful shutdown
process.on('SIGINT', () => {
    console.log('\nShutting down gracefully...');
    if (mqttClient) {
        mqttClient.end();
    }
    server.close(() => {
        console.log('Server closed');
        process.exit(0);
    });
});

module.exports = app;
