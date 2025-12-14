# Simulation Logic & Physics Engine

## 1. Time Scaling Strategy (The "Fast Clock")
To demonstrate a full day-night cycle and long-term soil monitoring within a short presentation window, the system uses an accelerated time scale.

* **Ratio:** 1 Real Second = 6 Virtual Minutes.
* **Update Frequency:** The simulation loop runs once every 1.0 real seconds.
* **Cycle Duration:**
    * 1 Virtual Hour = 10 Real Seconds.
    * 1 Virtual Day (24 Hours) = 240 Real Seconds (4 Minutes).

| Real Time | Virtual Time | Simulation Event |
| :--- | :--- | :--- |
| `00:00` (Start) | `06:00 AM` | Day begins, Sun rises. |
| `00:10` | `07:00 AM` | Morning heating begins. |
| `01:20` | `02:00 PM` | Peak temperature heat. |
| `02:00` | `06:00 PM` | Sun sets, Light drops. |
| `04:00` | `06:00 AM` | Next day begins. |

---

## 2. Environmental Physics Models

### A. Temperature Model (Sinusoidal Curve)
The temperature is not random; it follows a natural curve that mimics solar heating.
* **Formula:** $T = T_{base} + A \times \sin(\text{TimeOffset})$
* **Logic:**
    * Base Temperature ($T_{base}$): 20°C.
    * Amplitude ($A$): 10°C (Range is roughly 10°C to 30°C).
    * Peak Time: 14:00 (2:00 PM).
* **Noise:** A random fluctuation ($\pm 1.0^\circ C$) is added each tick to simulate natural sensor jitter.

### B. Lighting Model (Day/Night Cycle)
Lighting is determined strictly by the Virtual Hour.
* **Daytime:** `06:00` to `18:00`.
    * `is_day = True`
    * **Effect:** Dashboard shows Sun/Blue Sky. ML considers this high evaporation time.
* **Nighttime:** `18:00` to `06:00`.
    * `is_day = False`
    * **Effect:** Dashboard shows Moon/Dark Sky. Evaporation slows down.

---

## 3. Soil Moisture Dynamics (The Core Feedback Loop)
The soil moisture level ($M$) is the primary variable controlled by the system. It is affected by three factors: **Natural Evaporation**, **Temperature Stress**, and **Active Watering**.

### The Logic Step-by-Step (Per Tick):
1.  **Base Evaporation:**
    * Every virtual minute, moisture drops by a fixed rate (e.g., $0.5\%$ per tick).
    * $$M_{new} = M_{old} - (Rate \times \Delta t)$$

2.  **Diagnostic Stress Factor (Diagnostic Analytics):**
    * **Requirement:** "Whenever Temperature > 35°C, Soil Moisture drops 2x faster."
    * **Implementation:**
        ```python
        if Temperature > 35.0:
            evaporation_rate = base_rate * 2.0
        ```

3.  **Active Actuation (Watering):**
    * The system checks the Firebase path `plant_monitor/actuators/sprinkler_state`.
    * **If `True`:** The physics engine reverses the drop and adds moisture rapidly.
    * **Formula:** $$M_{new} = M_{old} + (\text{FillRate} \times \Delta t)$$
    * *(FillRate is set high, approx 3.0% per tick, to simulate a powerful pump).*

4.  **Clamping:**
    * Moisture is strictly limited between `0` (Bone Dry) and `100` (Saturated).

---

## 4. Machine Learning Implementation (Predictive Analytics)
The system uses **Linear Regression** to predict the specific time the plant will need water.

### Data Collection
* The Python script maintains a rolling buffer of `(Time, Moisture)` pairs for the current "Virtual Day."

### The Model
* **Algorithm:** Ordinary Least Squares (Linear Regression) via `scikit-learn`.
* **Input Features ($X$):** Virtual Time (in minutes).
* **Target Variable ($y$):** Moisture Level (%).

### The Prediction Goal
We want to find the time $t$ where moisture $y = 30$ (The Critical Threshold).
1.  Train model: $y = mx + c$ (Slope $m$, Intercept $c$).
2.  Solve for $x$ where $y = 30$:
    $$x_{critical} = \frac{30 - c}{m}$$
3.  **Output:** The system calculates `Time Remaining = x_critical - current_time` and displays it on the Dashboard as "Time to Empty: 2h 15m".

---

## 5. Alerting & States
The frontend visualizes the plant's health based on the `Moisture` value arriving via MQTT.

| Moisture Level | Plant State | Image Asset | Alert Status |
| :--- | :--- | :--- | :--- |
| **> 50%** | Healthy | `plant_healthy.png` | Nominal (Green) |
| **30% - 50%** | Sagging | `plant_sagging.png` | Warning (Yellow) |
| **< 30%** | Dead/Wilted | `plant_dead.png` | **CRITICAL (Red)** |