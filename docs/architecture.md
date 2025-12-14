# System Architecture: Smart Green IoT Simulation

## 1. Architectural Overview
The **Smart Green** system utilizes a **Hybrid IoT Architecture** that combines the speed of MQTT for real-time visualization with the reliability of a RESTful Cloud Database (Firebase) for state management and historical logging.

This decoupling allows the "Digital Twin" simulation to run smoothly (high frame rate) without overloading the database, while still maintaining a permanent record of environmental data.

## 2. System Diagram
The following diagram illustrates the data flow between the World Generator (Python), the Communication Layer, and the User Interface.

```mermaid
graph TD
    subgraph "Local Backend (The Farm)"
        A[Python World Generator] -->|Runs Logic| Physics(Physics Engine)
        A -->|Trains Model| ML(ML Predictor)
    end

    subgraph "Communication Layer"
        Physics -->|Publishes Telemetry (1Hz)| MQTT[MQTT Broker<br/>HiveMQ Public]
        Physics -->|Logs History (Hourly)| Firebase[Firebase Realtime DB]
        WebUI -->|Writes Actuator State| Firebase
    end

    subgraph "Frontend (The Dashboard)"
        MQTT -->|Subscribes (WebSockets)| WebUI[Web Dashboard<br/>HTML/JS]
        Firebase -->|Syncs State| WebUI
    end

    %% Data Flow Styling
    linkStyle 2 stroke:#0f0,stroke-width:2px,color:red; % MQTT Link
    linkStyle 3 stroke:#00f,stroke-width:2px; % Firebase Write
    linkStyle 4 stroke:#00f,stroke-width:2px; % Firebase Read
````

## 3\. Component Descriptions

### A. The "World Generator" (Backend)

  * **Role:** Acts as the central controller and virtual hardware. It replaces physical sensors (DHT11, FC-28) and the microcontroller (ESP8266/Arduino).
  * **Responsibilities:**
      * **Time Management:** Accelerates time (1 real second = 6 virtual minutes).
      * **Physics Simulation:** Calculates soil drying rates based on temperature and sun position.
      * **ML Processing:** Runs Linear Regression on buffered data to predict "Time to Dry".
      * **Telemetry Publishing:** Broadcasts the current state to MQTT.
      * **Actuator Polling:** Checks Firebase to see if the user has requested "Watering".

### B. The Communication Layer

This layer bridges the gap between the Python backend and the JavaScript frontend.

1.  **MQTT Broker (HiveMQ/Mosquitto)**

      * **Protocol:** MQTT over TCP (Python) and MQTT over WebSockets (Frontend).
      * **Purpose:** **Low-latency data streaming.** It carries the "Day Progress" (0-100%) and "Instant Moisture" values required for the smooth animation of the sun and plant.
      * **Topic:** `cs335/bese13ab/sensor_data`

2.  **Google Firebase (Realtime Database)**

      * **Protocol:** HTTPS (REST API).
      * **Purpose:** **State Persistence.**
          * Stores the official state of actuators (e.g., `sprinkler_state = true`).
          * Stores the historical log (`history_log`) for generating analytical charts.

### C. The "Digital Twin" (Frontend)

  * **Role:** The visual interface for the end-user.
  * **Responsibilities:**
      * **Visualization:** Renders the sky gradient, sun position, and plant health image based on MQTT data.
      * **Control:** Provides buttons to toggle actuators. When clicked, these write directly to Firebase.
      * **Alerting:** Displays critical warnings if moisture drops below the threshold (30%).

## 4\. Data Flow Scenarios

### Scenario 1: The "Heartbeat" (Every 1 Second)

1.  **Python** calculates new sun position and moisture.
2.  **Python** publishes JSON payload to MQTT topic.
3.  **Frontend** receives message via WebSocket.
4.  **Frontend** updates CSS (Sky color, Sun position) and Text (Clock).

### Scenario 2: The "Watering" Event (User Interaction)

1.  User clicks **"Turn On Sprinkler"** on the Web UI.
2.  **Web UI** updates `plant_monitor/actuators/sprinkler_state` to `true` in **Firebase**.
3.  **Python** (in its next loop) reads this `true` value from Firebase.
4.  **Python** physics engine drastically increases the moisture variable.
5.  **Python** publishes the new (higher) moisture to MQTT.
6.  **Frontend** receives the update and switches the plant image from "Sagging" to "Healthy".

