#!/bin/bash
# Smart Plant IoT System - Setup & Run Scripts

# Color codes for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Functions
print_header() {
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}═══════════════════════════════════════${NC}"
}

print_success() {
    echo -e "${GREEN}✓ $1${NC}"
}

print_error() {
    echo -e "${RED}✗ $1${NC}"
}

print_info() {
    echo -e "${YELLOW}ℹ $1${NC}"
}

# ==========================================
# 1. START MQTT BROKER ONLY
# ==========================================
start_mqtt_only() {
    print_header "Starting MQTT Broker Only"
    echo "This will start only the Mosquitto MQTT broker."
    echo "Services must be started separately."
    echo ""
    docker-compose up -d mosquitto
    
    if [ $? -eq 0 ]; then
        print_success "MQTT Broker started successfully"
        echo "Broker accessible at: mqtt://localhost:1883"
        echo "WebSocket available at: ws://localhost:9001"
    else
        print_error "Failed to start MQTT Broker"
        exit 1
    fi
}

# ==========================================
# 2. START ALL SERVICES (DOCKER)
# ==========================================
start_all_docker() {
    print_header "Starting All Services (Docker)"
    echo "This will start all 6 services in Docker containers."
    echo "Make sure Wokwi simulation is running!"
    echo ""
    
    print_info "Starting services..."
    docker-compose up -d
    
    if [ $? -eq 0 ]; then
        print_success "All services started"
        echo ""
        echo "Services running:"
        echo "  • MQTT Broker (mosquitto): localhost:1883"
        echo "  • Sensor Data Service: Processing sensor data"
        echo "  • Actuator Control Service: Managing actuators"
        echo "  • Firebase Service: Cloud sync"
        echo "  • Analytics Service: ML predictions"
        echo "  • Dashboard API: http://localhost:3000"
        echo ""
        echo "View logs: docker-compose logs -f"
        echo "Stop all: docker-compose down"
    else
        print_error "Failed to start services"
        exit 1
    fi
}

# ==========================================
# 3. START SERVICES LOCALLY (PYTHON)
# ==========================================
start_services_local() {
    print_header "Starting Services Locally (Development)"
    echo "You need 5 terminal windows for this method."
    echo "Follow the instructions below..."
    echo ""
    
    print_info "MQTT Broker (if not already running)"
    echo "docker-compose up -d mosquitto"
    echo ""
    
    print_info "Terminal 1 - Sensor Data Service"
    echo "cd services/sensor-data-service"
    echo "pip install -r requirements.txt"
    echo "python main.py"
    echo ""
    
    print_info "Terminal 2 - Actuator Control Service"
    echo "cd services/actuator-control"
    echo "pip install -r requirements.txt"
    echo "python main.py"
    echo ""
    
    print_info "Terminal 3 - Firebase Service"
    echo "cd services/firebase-service"
    echo "pip install -r requirements.txt"
    echo "python main.py"
    echo ""
    
    print_info "Terminal 4 - Analytics Service"
    echo "cd services/data-analytics"
    echo "pip install -r requirements.txt"
    echo "python main.py"
    echo ""
    
    print_info "Terminal 5 - Dashboard API"
    echo "cd dashboard/backend-api"
    echo "npm install"
    echo "npm start"
    echo ""
    
    print_success "Then open: http://localhost:3000"
}

# ==========================================
# 4. START WOKWI SIMULATION
# ==========================================
start_wokwi() {
    print_header "Starting Wokwi Simulation"
    echo "Follow these steps:"
    echo ""
    echo "1. Open VS Code"
    echo "2. Open folder: wokwi-simulation"
    echo "3. Open file: diagram.json"
    echo "4. Look for the Wokwi icon in the left sidebar"
    echo "5. Click the green play button to start simulation"
    echo ""
    print_success "Wokwi simulation started!"
}

# ==========================================
# 5. TEST MQTT
# ==========================================
test_mqtt() {
    print_header "Testing MQTT Connection"
    
    # Check if mosquitto_sub is available
    if ! command -v mosquitto_sub &> /dev/null; then
        print_error "mosquitto_sub not found. Install mosquitto client tools first."
        echo "Ubuntu/Debian: sudo apt-get install mosquitto-clients"
        echo "MacOS: brew install mosquitto"
        echo "Windows: https://mosquitto.org/download/"
        return
    fi
    
    print_info "Subscribing to all MQTT topics..."
    echo "Press Ctrl+C to stop."
    echo ""
    mosquitto_sub -h localhost -t "plant-iot/#" -v
}

# ==========================================
# 6. TEST API
# ==========================================
test_api() {
    print_header "Testing Dashboard API"
    
    print_info "Getting current data..."
    echo ""
    curl -s http://localhost:3000/api/data | python -m json.tool
    echo ""
    echo ""
    
    print_info "Getting predictions..."
    echo ""
    curl -s http://localhost:3000/api/predictions | python -m json.tool
    echo ""
    echo ""
    
    print_success "API tests completed"
}

# ==========================================
# 7. VIEW LOGS
# ==========================================
view_logs() {
    print_header "Docker Service Logs"
    
    echo "Select service to view logs:"
    echo "1) All services (follow)"
    echo "2) MQTT Broker"
    echo "3) Sensor Service"
    echo "4) Actuator Service"
    echo "5) Firebase Service"
    echo "6) Analytics Service"
    echo "7) Dashboard API"
    echo ""
    read -p "Enter choice (1-7): " choice
    
    case $choice in
        1) docker-compose logs -f ;;
        2) docker-compose logs -f mosquitto ;;
        3) docker-compose logs -f sensor-service ;;
        4) docker-compose logs -f actuator-service ;;
        5) docker-compose logs -f firebase-service ;;
        6) docker-compose logs -f analytics-service ;;
        7) docker-compose logs -f dashboard-api ;;
        *) print_error "Invalid choice" ;;
    esac
}

# ==========================================
# 8. STOP ALL SERVICES
# ==========================================
stop_all() {
    print_header "Stopping All Services"
    echo "Shutting down Docker services..."
    docker-compose down
    
    if [ $? -eq 0 ]; then
        print_success "All services stopped"
    else
        print_error "Error stopping services"
    fi
}

# ==========================================
# 9. HEALTH CHECK
# ==========================================
health_check() {
    print_header "System Health Check"
    
    echo "Checking MQTT Broker..."
    if docker ps | grep -q "mosquitto"; then
        print_success "MQTT Broker is running"
    else
        print_error "MQTT Broker is NOT running"
    fi
    
    echo ""
    echo "Checking Docker services..."
    docker-compose ps
    
    echo ""
    echo "Testing API..."
    if curl -s http://localhost:3000/api/data > /dev/null; then
        print_success "Dashboard API is responding"
    else
        print_error "Dashboard API is NOT responding"
    fi
    
    echo ""
    echo "Testing MQTT..."
    if timeout 2 mosquitto_sub -h localhost -t '$SYS/#' -C 1 > /dev/null 2>&1; then
        print_success "MQTT Broker is accepting connections"
    else
        print_error "MQTT Broker is NOT accepting connections"
    fi
}

# ==========================================
# 10. SEND MQTT COMMAND
# ==========================================
send_command() {
    print_header "Send MQTT Command"
    
    echo "Select actuator:"
    echo "1) Water Pump"
    echo "2) Cooling Fan"
    echo "3) Grow Light"
    echo ""
    read -p "Enter choice (1-3): " actuator
    
    echo ""
    echo "Select action:"
    echo "1) Turn ON"
    echo "2) Turn OFF"
    echo ""
    read -p "Enter choice (1-2): " action
    
    # Map selections
    case $actuator in
        1) topic="plant-iot/actuators/pump" ;;
        2) topic="plant-iot/actuators/fan" ;;
        3) topic="plant-iot/actuators/grow-light" ;;
        *) print_error "Invalid actuator"; return ;;
    esac
    
    case $action in
        1) cmd="ON" ;;
        2) cmd="OFF" ;;
        *) print_error "Invalid action"; return ;;
    esac
    
    print_info "Sending command..."
    mosquitto_pub -h localhost -t "$topic" -m "{\"action\": \"$cmd\"}"
    
    print_success "Command sent to $topic: $cmd"
}

# ==========================================
# MAIN MENU
# ==========================================
main_menu() {
    while true; do
        echo ""
        print_header "Smart Plant IoT System - Control Panel"
        echo ""
        echo "Setup & Start:"
        echo "  1) Start MQTT Broker only"
        echo "  2) Start ALL services (Docker) ⭐ Recommended"
        echo "  3) Start services locally (Development)"
        echo "  4) Start Wokwi Simulation (Manual)"
        echo ""
        echo "Testing & Monitoring:"
        echo "  5) Test MQTT connection"
        echo "  6) Test Dashboard API"
        echo "  7) View service logs"
        echo "  8) Health check"
        echo "  9) Send MQTT command"
        echo ""
        echo "Management:"
        echo "  10) Stop all services"
        echo "  11) Open Dashboard (http://localhost:3000)"
        echo "  0) Exit"
        echo ""
        read -p "Enter choice (0-11): " choice
        
        case $choice in
            1) start_mqtt_only ;;
            2) start_all_docker ;;
            3) start_services_local ;;
            4) start_wokwi ;;
            5) test_mqtt ;;
            6) test_api ;;
            7) view_logs ;;
            8) health_check ;;
            9) send_command ;;
            10) stop_all ;;
            11) 
                if command -v xdg-open &> /dev/null; then
                    xdg-open http://localhost:3000
                elif command -v open &> /dev/null; then
                    open http://localhost:3000
                else
                    echo "Open http://localhost:3000 in your browser"
                fi
                ;;
            0) 
                print_success "Goodbye!"
                exit 0
                ;;
            *)
                print_error "Invalid choice"
                ;;
        esac
    done
}

# ==========================================
# RUN MAIN MENU
# ==========================================
main_menu
