#!/bin/bash
# OpenClaw Agent Control Script for Linux/Mac

AGENT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYTHON=python3

# Couleurs
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

show_menu() {
    echo "========================================"
    echo "   OpenClaw Agent Controller"
    echo "========================================"
    echo ""
    echo -e "${GREEN}1.${NC} Demarrer l'agent"
    echo -e "${GREEN}2.${NC} Arreter l'agent"
    echo -e "${GREEN}3.${NC} Verifier le statut"
    echo -e "${GREEN}4.${NC} Initialiser la config"
    echo -e "${GREEN}5.${NC} Gestion n8n"
    echo -e "${GREEN}6.${NC} Voir les logs"
    echo -e "${GREEN}7.${NC} Demarrer le scheduler"
    echo -e "${GREEN}8.${NC} Quitter"
    echo ""
}

start_agent() {
    echo "Demarrage de l'agent..."
    nohup $PYTHON "$AGENT_DIR/agent.py" start > "$AGENT_DIR/agent.log" 2>&1 &
    echo "Agent demarre (PID: $!)"
    echo "Logs: $AGENT_DIR/agent.log"
}

stop_agent() {
    echo "Arret de l'agent..."
    pkill -f "agent.py"
    echo "Agent arrete."
}

check_status() {
    echo "========================================"
    echo "Status OpenClaw Agent"
    echo "========================================"
    
    if pgrep -f "agent.py" > /dev/null; then
        echo -e "Agent: ${GREEN}ACTIF${NC}"
    else
        echo -e "Agent: ${RED}INACTIF${NC}"
    fi
    
    if command -v docker &> /dev/null; then
        if docker ps -q -f name=n8n | grep -q .; then
            echo -e "n8n: ${GREEN}ACTIF${NC} (http://localhost:5678)"
        else
            echo -e "n8n: ${RED}ARRETE${NC}"
        fi
    fi
}

init_config() {
    echo "Initialisation..."
    $PYTHON "$AGENT_DIR/agent.py" init
}

show_n8n_menu() {
    while true; do
        echo ""
        echo "========================================"
        echo "   Gestion n8n"
        echo "========================================"
        echo ""
        echo "1. Demarrer n8n"
        echo "2. Arreter n8n"
        echo "3. Redemarrer n8n"
        echo "4. Voir les logs"
        echo "5. Retour"
        echo ""
        read -p "Choix: " choice
        
        case $choice in
            1)
                docker run -d --name n8n -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n 2>/dev/null || docker start n8n
                echo "n8n demarre sur http://localhost:5678"
                ;;
            2)
                docker stop n8n
                echo "n8n arrete."
                ;;
            3)
                docker restart n8n
                echo "n8n redemarre."
                ;;
            4)
                docker logs n8n -f --tail 50
                ;;
            5)
                break
                ;;
        esac
    done
}

view_logs() {
    if [ -f "$AGENT_DIR/agent.log" ]; then
        tail -f "$AGENT_DIR/agent.log"
    else
        echo "Aucun log trouve."
    fi
}

start_scheduler() {
    echo "Demarrage du scheduler..."
    nohup $PYTHON "$AGENT_DIR/scheduler.py" start > "$AGENT_DIR/scheduler.log" 2>&1 &
    echo "Scheduler demarre (PID: $!)"
}

# Menu principal
while true; do
    show_menu
    read -p "Choix: " choice
    
    case $choice in
        1) start_agent ;;
        2) stop_agent ;;
        3) check_status ;;
        4) init_config ;;
        5) show_n8n_menu ;;
        6) view_logs ;;
        7) start_scheduler ;;
        8) exit 0 ;;
        *) echo "Choix invalide." ;;
    esac
    
    echo ""
    read -p "Appuie sur Entree pour continuer..."
done
