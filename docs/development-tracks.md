# Smart Green IoT Farm Simulation - Development Tracks & Task Paths

## Project Overview
**Total Tasks**: 30 tasks across 3 parallel development tracks
**Development Approach**: Test-Driven Development (TDD) with comprehensive task granularity
**Integration Points**: Well-defined data contracts and timing synchronization

---

## **TRACK 1: Backend Developer A - Physics & ML Systems**
**Focus**: Core simulation engine, environmental physics, and predictive machine learning
**Total Tasks**: 14 tasks (including shared foundation)

### **Phase 1: Foundation Setup**
1. **Setup Backend Project Structure & Configuration** *(Shared with Track 2)*
   - Create backend directory structure
   - Setup Python logging and testing infrastructure
   - Configure dependencies (paho-mqtt, firebase-admin, scikit-learn)
   - Dependencies: None

### **Phase 2: Physics Engine Development (9 tasks)**

#### **Time & Environmental Systems**
2. **Implement Time Scaling System with TDD**
   - 1:6 time ratio (1 real second = 6 virtual minutes)
   - 240-second virtual day cycles starting at 06:00 AM
   - Dependencies: Backend Setup

3. **Develop Temperature Model with TDD**
   - Sinusoidal curve: T = 20 + 10*sin(time_offset)
   - Peak at 14:00, ±1.0°C noise, 10-30°C range
   - Dependencies: Time Scaling System

4. **Implement Day/Night Cycle with TDD**
   - Day: 06:00-18:00, Night: 18:00-06:00
   - Light intensity and day_progress calculations
   - Dependencies: Time Scaling System

#### **Moisture Dynamics & Integration**
5. **Create Moisture Dynamics System with TDD**
   - Base evaporation: 0.5% per tick
   - Heat stress: 2x multiplier when >35°C
   - Sprinkler effect: +3% per tick
   - Dependencies: Temperature Model

6. **Integrate Physics Engine Components with TDD**
   - Master PhysicsEngine coordinator class
   - 1Hz simulation timing, component coordination
   - Dependencies: Moisture System + Day/Night Cycle

### **Phase 3: Machine Learning Pipeline (4 tasks)**

#### **ML Infrastructure**
7. **Create ML Data Buffer Management with TDD**
   - Rolling buffer for (time_index, moisture_level) pairs
   - Memory management, day boundary resets
   - Dependencies: Backend Setup

8. **Develop ML Training Engine with TDD**
   - scikit-learn Linear Regression implementation
   - Retraining every virtual hour (10 real seconds)
   - Dependencies: ML Buffer Management

#### **Prediction & Integration**
9. **Implement ML Prediction Logic with TDD**
   - Predict 30% moisture threshold timing
   - "Xh Ym" output formatting, edge case handling
   - Dependencies: ML Training Engine

10. **Integrate Complete ML System with TDD**
    - Unified MLPredictor pipeline coordinator
    - Integration with physics timing system
    - Dependencies: ML Prediction Logic + Physics Integration

---

## **TRACK 2: Backend Developer B - Communication & Integration**
**Focus**: Network protocols, database integration, and system orchestration
**Total Tasks**: 10 tasks (including shared foundation)

### **Phase 1: Foundation Setup**
1. **Setup Backend Project Structure & Configuration** *(Shared with Track 1)*
   - Same foundation task as Track 1
   - Dependencies: None

### **Phase 2: MQTT Communication System (4 tasks)**

#### **MQTT Infrastructure**
2. **Create MQTT Connection Management with TDD**
   - Public broker integration (broker.hivemq.com)
   - Connection retry logic with exponential backoff
   - Dependencies: Backend Setup

3. **Implement MQTT Payload Schema with TDD**
   - Exact JSON schema validation (moisture, temperature, day_progress, etc.)
   - Frontend compatibility and data integrity
   - Dependencies: Backend Setup

#### **MQTT Operations**
4. **Develop MQTT Publishing Engine with TDD**
   - Precise 1Hz telemetry broadcasting
   - Topic: cs335/bese13ab/sensor_data
   - Dependencies: MQTT Connection + Payload Schema

5. **Integrate Complete MQTT Client with TDD**
   - Master MQTT coordinator
   - Physics engine integration for data flow
   - Dependencies: MQTT Publishing Engine

### **Phase 3: Firebase Integration System (4 tasks)**

#### **Firebase Infrastructure**
6. **Create Firebase Authentication & Connection with TDD**
   - Service account authentication
   - Firebase Realtime Database connection
   - Dependencies: Backend Setup

7. **Implement Firebase Actuator State Management with TDD**
   - Bidirectional actuator control (sprinkler, lights, fan)
   - Real-time listeners for dashboard commands
   - Database: plant_monitor/actuators/ branch
   - Dependencies: Firebase Authentication

#### **Firebase Operations**
8. **Develop Firebase Historical Logging with TDD**
   - Environmental data logging every virtual hour
   - Database: plant_monitor/history_log/ branch
   - Dependencies: Firebase Authentication

9. **Integrate Complete Firebase Client with TDD**
   - Master Firebase coordinator
   - Actuator sync + Historical logging coordination
   - Dependencies: Firebase Actuator Management + Historical Logging

### **Phase 4: System Integration**
10. **Integrate Backend Main Loop with Integration Tests**
    - Master simulation coordinator
    - Physics + ML + MQTT + Firebase orchestration
    - End-to-end testing and error isolation
    - Dependencies: Complete Physics System + ML System + MQTT Client + Firebase Client

---

## **TRACK 3: Frontend Developer - Web Dashboard**
**Focus**: Digital twin visualization, user interface, and real-time data presentation
**Total Tasks**: 6 tasks

### **Phase 1: Foundation Setup**
1. **Setup Frontend Project Structure**
   - HTML5 dashboard, modular CSS architecture
   - JavaScript module organization
   - Dependencies: None

### **Phase 2: Communication Integration (2 tasks)**
2. **Develop MQTT WebSocket Handler**
   - JavaScript MQTT client for real-time telemetry
   - WebSocket connection to same broker as backend
   - Dependencies: Frontend Setup

3. **Implement Firebase Web Integration**
   - Firebase Web SDK for actuator commands
   - Historical data retrieval for analytics
   - Dependencies: Frontend Setup

### **Phase 3: Visualization Engine (2 tasks)**
4. **Create Digital Twin Visualization Engine**
   - Sky gradients, sun/moon movement, plant health states
   - CSS animations synchronized with telemetry data
   - Dependencies: Frontend Setup + MQTT Handler

5. **Build Interactive Dashboard Controls**
   - Actuator controls (sprinkler, lights, fan)
   - Data displays, alert systems, visual feedback
   - Dependencies: Frontend Setup + Firebase Integration + MQTT Handler

### **Phase 4: Application Coordination**
6. **Integrate Frontend Application Coordination**
   - Master AppCoordinator for all frontend modules
   - State management, error boundaries, lifecycle management
   - Dependencies: Visualization Engine + Dashboard Controls

---

## **FINAL INTEGRATION PHASE**
**Shared by All Tracks**

**Complete Documentation & Project Setup**
- Comprehensive README, setup guides, VS Code configuration
- Troubleshooting documentation, deployment guides
- Dependencies: Backend Integration + Frontend Coordination

---

## **Development Timeline & Dependencies**

### **Parallel Development Phases**

#### **Phase 1: Foundation (Week 1)**
- **All Tracks**: Setup project structures simultaneously
- **Track 1**: Begin Time Scaling System
- **Track 2**: Begin MQTT Connection Management  
- **Track 3**: Begin MQTT WebSocket Handler

#### **Phase 2: Core Development (Weeks 2-3)**
- **Track 1**: Physics Engine development (Temperature → Day/Night → Moisture → Integration)
- **Track 2**: Communication protocols (MQTT Pipeline → Firebase Pipeline)
- **Track 3**: Visualization components (Digital Twin Engine → Dashboard Controls)

#### **Phase 3: ML & Integration (Week 4)**
- **Track 1**: ML Pipeline development (Buffer → Training → Prediction → Integration)
- **Track 2**: System integration (Backend Main Loop)
- **Track 3**: Application coordination

#### **Phase 4: Final Integration (Week 5)**
- **All Tracks**: Complete Documentation & Project Setup
- End-to-end testing and deployment preparation

### **Critical Path Dependencies**
1. **Backend Setup** → All backend development
2. **Physics Engine** → ML System Integration → Backend Main Loop
3. **MQTT Client** → Backend Main Loop
4. **Firebase Client** → Backend Main Loop  
5. **Frontend Coordination** → Final Documentation

### **Integration Points**
- **Data Contracts**: MQTT JSON payload, Firebase database schema
- **Timing Synchronization**: 1Hz MQTT telemetry, virtual hour Firebase logging
- **Error Isolation**: Network failures don't crash simulation
- **Performance Requirements**: <2s UI latency, smooth animations

---

## **Task Distribution Summary**

| Track | Developer Focus | Task Count | Key Technologies |
|-------|----------------|------------|------------------|
| **Track 1** | Backend A: Physics & ML | 10 tasks | Python, Physics Simulation, scikit-learn |
| **Track 2** | Backend B: Communication | 9 tasks | MQTT, Firebase, Network Protocols |
| **Track 3** | Frontend: Dashboard | 6 tasks | HTML5, CSS3, JavaScript, WebSockets |
| **Integration** | All Tracks | 1 task | Documentation, Setup, Deployment |
| **Total** | **3 Developers** | **30 tasks** | **Full IoT Stack** |

This structure enables efficient parallel development while maintaining clear integration points and comprehensive test coverage throughout the development process.