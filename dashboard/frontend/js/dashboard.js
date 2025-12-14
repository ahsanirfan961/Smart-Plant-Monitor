/* Dashboard JavaScript - Real-time data visualization */

// Configuration - Use current window location for dynamic URLs
// Backend server runs on port 3003
const BACKEND_PORT = 3003;
const API_BASE = `${window.location.protocol}//${window.location.hostname}:${BACKEND_PORT}/api`;
const SOCKET_URL = `${window.location.protocol}//${window.location.hostname}:${BACKEND_PORT}`;

// Global state
let currentData = {
    sensors: {
        temperature: 0,
        humidity: 0,
        soil_moisture: 0,
        light_intensity: 0
    },
    actuators: {
        pump: 'OFF',
        fan: 'OFF',
        grow_light: 'OFF'
    },
    predictions: {
        dryness: {},
        health: {}
    }
};

let charts = {};
let gauges = {};
let socket;
let lastAlertTime = 0;  // Track last alert to prevent spam

// Initialize on page load
document.addEventListener('DOMContentLoaded', function () {
    initializeConnection();
    initializeGauges();
    initializeCharts();
    fetchInitialData();
});

/* ========== Connection Management ========== */

function initializeConnection() {
    // Connect via Socket.IO for real-time updates
    socket = io(SOCKET_URL, {
        reconnection: true,
        reconnectionDelay: 1000,
        reconnectionDelayMax: 5000,
        reconnectionAttempts: 5
    });

    socket.on('connect', () => {
        console.log('Connected to server');
        updateConnectionStatus(true);
    });

    socket.on('disconnect', () => {
        console.log('Disconnected from server');
        updateConnectionStatus(false);
    });

    socket.on('sensor-data', (data) => {
        updateSensorData(data);
    });

    socket.on('actuator-status', (data) => {
        updateActuatorStatus(data);
    });

    socket.on('predictions', (data) => {
        updatePredictions(data);
    });

    socket.on('alert', (data) => {
        addAlert(data);
    });

    socket.on('error', (error) => {
        console.error('Socket error:', error);
        addAlert({ type: 'danger', message: 'Connection error: ' + error });
    });
}

function updateConnectionStatus(connected) {
    const indicator = document.getElementById('connectionStatus');
    const text = document.getElementById('connectionText');

    if (connected) {
        indicator.classList.add('connected');
        text.textContent = 'Connected';
    } else {
        indicator.classList.remove('connected');
        text.textContent = 'Disconnected';
    }
}

/* ========== Gauge Initialization ========== */

function initializeGauges() {
    // Temperature Gauge
    gauges.temp = createLinearGauge('tempGauge', {
        min: -10,
        max: 50,
        value: 24,
        color: '#3498db'
    });

    // Humidity Gauge
    gauges.humidity = createLinearGauge('humidityGauge', {
        min: 0,
        max: 100,
        value: 65,
        color: '#2ecc71'
    });

    // Moisture Gauge
    gauges.moisture = createLinearGauge('moistureGauge', {
        min: 0,
        max: 100,
        value: 50,
        color: '#e74c3c'
    });

    // Light Gauge
    gauges.light = createLinearGauge('lightGauge', {
        min: 0,
        max: 100,
        value: 50,
        color: '#f39c12'
    });
}

function createLinearGauge(canvasId, options) {
    const canvas = document.getElementById(canvasId);
    const ctx = canvas.getContext('2d');

    return {
        canvas: canvas,
        ctx: ctx,
        ...options,
        update: function (value) {
            this.value = value;
            drawGauge(this);
        }
    };
}

function drawGauge(gauge) {
    const canvas = gauge.canvas;
    const ctx = gauge.ctx;
    const size = 150;

    // Clear canvas
    ctx.clearRect(0, 0, size, size);

    // Draw background circle
    ctx.fillStyle = '#ecf0f1';
    ctx.beginPath();
    ctx.arc(size / 2, size / 2, size / 2 - 5, 0, 2 * Math.PI);
    ctx.fill();

    // Draw value arc
    const range = gauge.max - gauge.min;
    const percent = (gauge.value - gauge.min) / range;
    const startAngle = Math.PI * 1.2;
    const endAngle = startAngle + (percent * Math.PI * 1.6);

    ctx.strokeStyle = gauge.color;
    ctx.lineWidth = 8;
    ctx.lineCap = 'round';
    ctx.beginPath();
    ctx.arc(size / 2, size / 2, size / 2 - 15, startAngle, endAngle);
    ctx.stroke();

    // Draw text
    ctx.fillStyle = '#2c3e50';
    ctx.font = 'bold 24px Arial';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'middle';
    ctx.fillText(gauge.value.toFixed(1), size / 2, size / 2);
}

/* ========== Chart Initialization ========== */

function initializeCharts() {
    const chartOptions = {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
            legend: {
                display: false
            }
        },
        scales: {
            y: {
                beginAtZero: true
            }
        }
    };

    // Temperature Chart
    charts.temp = createChart('tempChart', {
        label: 'Temperature (°C)',
        color: '#3498db',
        ...chartOptions
    });

    // Humidity Chart
    charts.humidity = createChart('humidityChart', {
        label: 'Humidity (%)',
        color: '#2ecc71',
        ...chartOptions
    });

    // Moisture Chart
    charts.moisture = createChart('moistureChart', {
        label: 'Soil Moisture (%)',
        color: '#e74c3c',
        ...chartOptions
    });

    // Light Chart
    charts.light = createChart('lightChart', {
        label: 'Light Intensity (%)',
        color: '#f39c12',
        ...chartOptions
    });

    // Initialize with empty data
    const labels = generateTimeLabels(24);
    updateChartData('temp', labels, Array(24).fill(null));
    updateChartData('humidity', labels, Array(24).fill(null));
    updateChartData('moisture', labels, Array(24).fill(null));
    updateChartData('light', labels, Array(24).fill(null));
}

function createChart(canvasId, options) {
    const ctx = document.getElementById(canvasId).getContext('2d');
    return new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: options.label,
                data: [],
                borderColor: options.color,
                backgroundColor: options.color + '20',
                borderWidth: 2,
                tension: 0.4,
                fill: true,
                pointRadius: 3,
                pointBackgroundColor: options.color,
                pointBorderColor: '#fff',
                pointBorderWidth: 2
            }]
        },
        options: options
    });
}

function generateTimeLabels(hours) {
    const labels = [];
    for (let i = hours - 1; i >= 0; i--) {
        const time = new Date();
        time.setHours(time.getHours() - i);
        labels.push(time.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' }));
    }
    return labels;
}

function updateChartData(chartKey, labels, data) {
    if (charts[chartKey]) {
        charts[chartKey].data.labels = labels;
        charts[chartKey].data.datasets[0].data = data;
        charts[chartKey].update();
    }
}

/* ========== Data Update Functions ========== */

function fetchInitialData() {
    // Fetch current data via API
    fetch(`${API_BASE}/data`)
        .then(response => response.json())
        .then(data => {
            updateSensorData(data.sensors);
            updateActuatorStatus(data.actuators);
        })
        .catch(error => console.error('Error fetching data:', error));

    // Fetch predictions
    fetch(`${API_BASE}/predictions`)
        .then(response => response.json())
        .then(data => {
            updatePredictions(data);
        })
        .catch(error => console.error('Error fetching predictions:', error));

    // Fetch history
    fetch(`${API_BASE}/history?hours=24`)
        .then(response => response.json())
        .then(data => {
            updateCharts(data);
        })
        .catch(error => console.error('Error fetching history:', error));
}

function updateSensorData(sensorData) {
    currentData.sensors = sensorData;

    // Update gauges
    gauges.temp.update(sensorData.temperature);
    gauges.humidity.update(sensorData.humidity);
    gauges.moisture.update(sensorData.soil_moisture);
    gauges.light.update(sensorData.light_intensity);

    // Update display values
    document.getElementById('tempValue').textContent = sensorData.temperature.toFixed(1) + ' °C';
    document.getElementById('humidityValue').textContent = sensorData.humidity.toFixed(1) + ' %';
    document.getElementById('moistureValue').textContent = sensorData.soil_moisture.toFixed(1) + ' %';
    document.getElementById('lightValue').textContent = sensorData.light_intensity.toFixed(1) + ' %';

    // Update charts with new data point
    updateChartsWithNewData(sensorData);

    updateLastUpdate();
}

function updateChartsWithNewData(sensorData) {
    // Handle timestamp - could be in milliseconds or seconds
    let timestamp;
    if (sensorData.timestamp) {
        const ts = sensorData.timestamp;
        // If timestamp is in milliseconds (> 10^10), convert it; otherwise assume seconds
        timestamp = new Date(ts > 10000000000 ? ts : ts * 1000);
    } else {
        timestamp = new Date();
    }
    
    const timeLabel = timestamp.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });

    // Add new data points to each chart
    [
        { chart: 'temp', data: sensorData.temperature },
        { chart: 'humidity', data: sensorData.humidity },
        { chart: 'moisture', data: sensorData.soil_moisture },
        { chart: 'light', data: sensorData.light_intensity }
    ].forEach(item => {
        const chart = charts[item.chart];
        if (chart) {
            // Add new label
            chart.data.labels.push(timeLabel);
            // Add new data point
            chart.data.datasets[0].data.push(item.data);

            // Keep only last 24 hours of data (288 points for 5-minute intervals)
            const maxPoints = 288;
            if (chart.data.labels.length > maxPoints) {
                chart.data.labels.shift();
                chart.data.datasets[0].data.shift();
            }

            // Update the chart
            chart.update();
        }
    });
}

function updateActuatorStatus(actuatorData) {
    currentData.actuators = actuatorData;
    console.log('Updating actuator status:', actuatorData);

    // Update actuator status displays
    updateActuatorDisplay('pump', actuatorData.pump);
    updateActuatorDisplay('fan', actuatorData.fan);
    updateActuatorDisplay('grow_light', actuatorData.grow_light);
}

function updateActuatorDisplay(actuator, status) {
    // Normalize status: handle 'ON', true, 1 as active; 'OFF', false, 0 as inactive
    const isOn = status === 'ON' || status === true || status === 1;
    const statusText = isOn ? 'ON' : 'OFF';
    const indicator = isOn ? '● ON' : '○ OFF';  // Filled bullet for ON, empty bullet for OFF
    
    const statusElement = document.getElementById(
        actuator === 'grow_light' ? 'lightStatus' : actuator + 'Status'
    );
    
    if (statusElement) {
        statusElement.textContent = indicator;
        statusElement.className = 'status ' + (isOn ? 'on' : 'off');
        console.log(`${actuator} status updated to: ${indicator}`);
    }
}

function updatePredictions(predictionData) {
    currentData.predictions = predictionData;

    // Guard against undefined data
    if (!predictionData) {
        console.log('No prediction data available');
        return;
    }

    // Update dryness prediction
    if (predictionData.dryness && predictionData.dryness.eta_hours !== undefined) {
        const dryness = predictionData.dryness;
        document.getElementById('drynessETA').textContent = dryness.eta_hours.toFixed(1) + ' hours';
        document.getElementById('drynessRec').textContent = dryness.recommendation || 'N/A';
        document.getElementById('drynessConf').textContent = ((dryness.confidence || 0) * 100).toFixed(0) + '%';
    } else {
        document.getElementById('drynessETA').textContent = 'Calculating...';
        document.getElementById('drynessRec').textContent = 'Waiting for data';
        document.getElementById('drynessConf').textContent = '0%';
    }

    // Update health score
    if (predictionData.health && predictionData.health.score !== undefined) {
        const health = predictionData.health;
        document.getElementById('healthScore').textContent = health.score.toFixed(0);
        document.getElementById('healthClass').textContent = health.classification || 'Unknown';

        // Update recommendations
        const recList = document.getElementById('recommendationsList');
        recList.innerHTML = '';
        if (health.recommendations && health.recommendations.length > 0) {
            health.recommendations.forEach(rec => {
                const li = document.createElement('li');
                li.textContent = rec;
                recList.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.textContent = 'Plant is healthy!';
            recList.appendChild(li);
        }
    }
}

function updateCharts(historyData) {
    if (!historyData || historyData.length === 0) return;

    const labels = historyData.map(d => new Date(d.timestamp).toLocaleTimeString());
    const tempData = historyData.map(d => d.temperature);
    const humidityData = historyData.map(d => d.humidity);
    const moistureData = historyData.map(d => d.soil_moisture);
    const lightData = historyData.map(d => d.light_intensity);

    updateChartData('temp', labels, tempData);
    updateChartData('humidity', labels, humidityData);
    updateChartData('moisture', labels, moistureData);
    updateChartData('light', labels, lightData);
}

function updateLastUpdate() {
    const now = new Date();
    const timeString = now.toLocaleTimeString('en-US', {
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: true
    });
    document.getElementById('lastUpdate').textContent = timeString;
}

/* ========== Actuator Control ========== */

function controlActuator(actuator, action) {
    const endpoint = actuator === 'grow-light' ? 'grow_light' : actuator;

    fetch(`${API_BASE}/command/${endpoint}`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            action: action,
            duration: 0  // 0 = indefinite
        })
    })
        .then(response => response.json())
        .then(data => {
            console.log('Command sent:', data);
            addAlert({
                type: 'success',
                message: `${actuator} turned ${action}`
            });
        })
        .catch(error => {
            console.error('Error sending command:', error);
            addAlert({
                type: 'danger',
                message: 'Failed to send command'
            });
        });
}

/* ========== Alerts ========== */

function addAlert(alertData) {
    // Throttle warning/anomaly alerts to prevent spam (max 1 per 5 seconds)
    if (alertData.type === 'warning') {
        const now = Date.now();
        if (now - lastAlertTime < 5000) {
            return;  // Skip this alert
        }
        lastAlertTime = now;
    }

    const container = document.getElementById('alertsContainer');
    const alertDiv = document.createElement('div');
    alertDiv.className = `alert-item alert-${alertData.type}`;
    alertDiv.textContent = alertData.message || 'System alert';

    container.insertBefore(alertDiv, container.firstChild);

    // Keep only last 10 alerts
    while (container.children.length > 10) {
        container.removeChild(container.lastChild);
    }

    // Auto-remove success alerts after 5 seconds, warning after 10 seconds
    if (alertData.type === 'success') {
        setTimeout(() => {
            alertDiv.remove();
        }, 5000);
    } else if (alertData.type === 'warning') {
        setTimeout(() => {
            alertDiv.remove();
        }, 10000);
    }
}

/* ========== Update Loop ========== */

// Fetch data every 30 seconds
setInterval(() => {
    fetchInitialData();
}, 30000);

// Update gauges immediately on socket data
socket.on('sensor-update', (data) => {
    updateSensorData(data);
});
