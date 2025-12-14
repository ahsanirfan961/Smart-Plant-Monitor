# Project Requirements: Smart Green IoT Farm Simulation

## 1. Project Overview
**Project Title:** Smart Green: IoT-Based Environmental Monitoring & Automation System
**Project Type:** Software-Only "Digital Twin" Simulation
**Target Audience:** University Instructor (CS335: Internet of Things)
**Core Concept:** A "gamified" simulation of a smart farm environment that uses virtual sensors and actuators to manage plant health. The system runs on a "Fast Clock" (accelerated time) to demonstrate long-term monitoring and automation in a short demo window.

## 2. System Purpose & Objectives
The goal is to demonstrate a fully functional IoT feedback loop without physical hardware.
* **Monitor:** Continuously track soil moisture, temperature, and light intensity in a virtual environment.
* **Analyze:** Use real-time Machine Learning (Linear Regression) to predict when the soil will become critically dry.
* **Act:** Automate responses (e.g., turn on virtual sprinkler) based on sensor thresholds.
* **Visualize:** Provide a highly engaging "Digital Twin" web dashboard with smooth day/night cycles and animated plant health states.

## 3. High-Level Architecture
The system follows a "Hybrid Architecture" utilizing three distinct communication layers:
1.  **Simulation Backend (Python):** The "World Generator" that simulates physics, runs ML models, and acts as the sensor node.
2.  **Live Telemetry (MQTT):** High-frequency data transmission for smooth animations on the frontend.
3.  **Data Persistence (Firebase):** REST API usage for storing historical data and syncing actuator states.

## 4. Functional Requirements

### 4.1. The "World Generator" (Backend)
* **Technology:** Python 3.9+
* **Time Scaling:** The simulation must run on accelerated time.
    * **Ratio:** 1 Real Second = 6 Virtual Minutes.
    * **Cycle:** A full 24-hour day completes in 240 real seconds (4 minutes).
* **Physics Engine:**
    * **Sun/Moon:** Calculate `day_progress` (0-100%) to drive light levels and UI animation.
    * **Temperature:** Simulate a curve peaking at 14:00 (2 PM) and dropping at night.
    * **Moisture:** Natural drying occurs every virtual minute.
        * *Diagnostic Logic:* If `Temperature > 35°C`, the drying rate must **double** (2x multiplier).
    * **Actuation:** If the Sprinkler is ON, moisture level must rise rapidly.
* **Machine Learning (Real-Time):**
    * **Algorithm:** Linear Regression (`scikit-learn`).
    * **Input:** Historical moisture data collected during the current virtual session.
    * **Output:** Predict the specific "Time to Dry" (time remaining until moisture hits 30%).
    * **Frequency:** Retrain/Predict once every virtual hour.

### 4.2. Communication Protocols
* **MQTT (Telemetry):**
    * **Role:** Transmit high-speed data for the Web UI animation.
    * **Broker:** Public Broker (e.g., `broker.hivemq.com` or `test.mosquitto.org`).
    * **Topic:** `cs335/bese13ab/sensor_data` (or similar unique path).
    * **Payload:** JSON containing `moisture`, `temp`, `day_progress`, `is_day`, `prediction`.
    * **Update Rate:** 1 Hz (Every 1 real second).
* **Firebase Realtime Database (Persistence):**
    * **Role:** Store actuator command states and historical logs.
    * **Node 1 (`actuators`):** Read by Python to check if Sprinkler/Lights are ON.
    * **Node 2 (`history_log`):** Written by Python once per virtual hour for line charts.

### 4.3. The "Digital Twin" Dashboard (Frontend)
* **Technology:** HTML5, CSS3, JavaScript (Vanilla).
* **Connectivity:**
    * Must use `Paho MQTT` over WebSockets to subscribe to the Python backend.
    * Must use `Firebase SDK` to write actuator commands (button clicks).
* **Visual Requirements:**
    * **Sky Animation:** A visual sky that transitions smoothly (CSS Gradients) from Blue (Day) to Black (Night) based on MQTT `day_progress`.
    * **Sun/Moon Movement:** A celestial body that moves in an arc across the screen, synchronized with virtual time.
    * **Plant Health:** Dynamic image switching:
        * `Healthy`: Moisture > 50%
        * `Sagging`: Moisture 30-50%
        * `Dead/Wilted`: Moisture < 30%
* **Controls:**
    * **Sprinkler Button:** A toggle button that updates Firebase. Visual feedback (water animation) must appear when active.

## 5. Non-Functional Requirements
* **Latency:** Visual updates on the dashboard must appear within < 2 seconds of the backend change.
* **Resilience:** The Python script must handle network disconnects (MQTT/Firebase) gracefully without crashing.
* **Deployment:** The system is designed to run on **Localhost**.

## 6. Key Deliverables & Tech Stack
| Component | Technology | Libraries/Tools |
| :--- | :--- | :--- |
| **Backend** | Python | `paho-mqtt`, `firebase-admin`, `scikit-learn`, `pandas`, `numpy` |
| **Frontend** | Web (HTML/JS) | `paho-mqtt.js` (WebSockets), Chart.js (Optional), Firebase JS SDK |
| **Broker** | MQTT | HiveMQ Public Broker (Port 1883 for Py, 8000 for JS) |
| **Database** | NoSQL | Google Firebase Realtime Database |

## 7. Logic Constraints & Rules
1.  **Moisture Range:** 0% (Bone Dry) to 100% (Saturated).
2.  **Dry Threshold:** < 30% triggers the "Critical" alert and "Dead" plant image.
3.  **Temperature Range:** 15°C to 40°C (Simulated).
4.  **Lighting:**
    * Day: 06:00 to 18:00 (High Lux).
    * Night: 18:00 to 06:00 (Low Lux).