#!/usr/bin/env python3
"""
OpenClaw Agent Autonome
Surveille et execute des taches automatiquement
"""

import subprocess
import time
import json
import os
from datetime import datetime
from pathlib import Path

# Configuration
AGENT_DIR = Path(__file__).parent
LOG_FILE = AGENT_DIR / "agent.log"
CONFIG_FILE = AGENT_DIR / "agent-config.json"
TASKS_FILE = AGENT_DIR / "tasks.json"


class OpenClawAgent:
    def __init__(self):
        self.running = False
        self.tasks = []
        self.load_config()
        
    def load_config(self):
        """Charge la configuration"""
        if CONFIG_FILE.exists():
            with open(CONFIG_FILE, 'r') as f:
                self.config = json.load(f)
        else:
            self.config = {
                "check_interval": 60,  # Verifie toutes les 60 secondes
                "notifications": True,
                "services_to_monitor": ["docker", "n8n"]
            }
            self.save_config()
    
    def save_config(self):
        """Sauvegarde la configuration"""
        with open(CONFIG_FILE, 'w') as f:
            json.dump(self.config, f, indent=2)
    
    def log(self, message):
        """Log un message"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] {message}"
        print(log_entry)
        with open(LOG_FILE, 'a') as f:
            f.write(log_entry + "\n")
    
    def check_service(self, service_name):
        """Verifie si un service tourne"""
        try:
            if service_name == "docker":
                result = subprocess.run(
                    ["docker", "ps"], 
                    capture_output=True, 
                    text=True, 
                    timeout=5
                )
                return result.returncode == 0
            elif service_name == "n8n":
                result = subprocess.run(
                    ["docker", "ps", "-q", "-f", "name=n8n"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                return result.stdout.strip() != ""
        except Exception as e:
            self.log(f"Erreur verification {service_name}: {e}")
            return False
    
    def execute_command(self, command):
        """Execute une commande et retourne le resultat"""
        try:
            self.log(f"Execution: {command}")
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "code": result.returncode
            }
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def start_n8n(self):
        """Demarre n8n si pas deja actif"""
        if not self.check_service("n8n"):
            self.log("Demarrage de n8n...")
            cmd = """docker run -d --name n8n -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n"""
            result = self.execute_command(cmd)
            if result["success"]:
                self.log("n8n demarre avec succes")
                return True
            else:
                self.log(f"Erreur demarrage n8n: {result.get('stderr', result.get('error'))}")
                return False
        else:
            self.log("n8n est deja actif")
            return True
    
    def stop_n8n(self):
        """Arrete n8n"""
        self.log("Arret de n8n...")
        cmd = "docker stop n8n && docker rm n8n"
        result = self.execute_command(cmd)
        return result["success"]
    
    def run_docker_compose(self, compose_file):
        """Execute docker-compose"""
        if not os.path.exists(compose_file):
            return {"success": False, "error": f"Fichier non trouve: {compose_file}"}
        
        cmd = f"docker-compose -f {compose_file} up -d"
        return self.execute_command(cmd)
    
    def process_task(self, task):
        """Traite une tache"""
        task_type = task.get("type")
        self.log(f"Traitement tache: {task_type}")
        
        if task_type == "start_n8n":
            return self.start_n8n()
        elif task_type == "stop_n8n":
            return self.stop_n8n()
        elif task_type == "docker_compose":
            return self.run_docker_compose(task.get("file"))
        elif task_type == "command":
            return self.execute_command(task.get("command"))
        elif task_type == "check_services":
            services = task.get("services", self.config["services_to_monitor"])
            results = {}
            for svc in services:
                results[svc] = self.check_service(svc)
            return results
        else:
            return {"success": False, "error": f"Type inconnu: {task_type}"}
    
    def monitor_loop(self):
        """Boucle principale de surveillance"""
        self.log("Agent demarre - Mode surveillance")
        
        while self.running:
            try:
                # Verifie les services
                for service in self.config["services_to_monitor"]:
                    status = self.check_service(service)
                    if not status:
                        self.log(f"ALERTE: {service} n'est pas actif!")
                        # Redemarre automatiquement si configure
                        if service == "n8n" and self.config.get("auto_restart", False):
                            self.start_n8n()
                
                # Verifie s'il y a des taches a executer
                if TASKS_FILE.exists():
                    with open(TASKS_FILE, 'r') as f:
                        tasks = json.load(f)
                    
                    for task in tasks:
                        self.process_task(task)
                    
                    # Supprime les taches traitees
                    TASKS_FILE.unlink()
                
                # Attend avant prochaine verification
                time.sleep(self.config["check_interval"])
                
            except Exception as e:
                self.log(f"Erreur dans la boucle: {e}")
                time.sleep(5)
    
    def start(self):
        """Demarre l'agent"""
        self.running = True
        self.log("=" * 50)
        self.log("OpenClaw Agent demarre")
        self.log("=" * 50)
        self.monitor_loop()
    
    def stop(self):
        """Arrete l'agent"""
        self.running = False
        self.log("Agent arrete")


def create_sample_config():
    """Cree une configuration par defaut"""
    config = {
        "check_interval": 60,
        "notifications": True,
        "auto_restart": True,
        "services_to_monitor": ["docker", "n8n"],
        "webhook_url": None
    }
    
    with open(CONFIG_FILE, 'w') as f:
        json.dump(config, f, indent=2)
    
    print(f"Configuration creee: {CONFIG_FILE}")


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "init":
            create_sample_config()
        elif sys.argv[1] == "start":
            agent = OpenClawAgent()
            try:
                agent.start()
            except KeyboardInterrupt:
                agent.stop()
        elif sys.argv[1] == "task":
            # Execute une tache unique
            if len(sys.argv) > 2:
                task = {"type": sys.argv[2], "command": " ".join(sys.argv[3:]) if len(sys.argv) > 3 else None}
                agent = OpenClawAgent()
                result = agent.process_task(task)
                print(json.dumps(result, indent=2))
    else:
        print("Usage:")
        print("  python agent.py init          - Cree la configuration")
        print("  python agent.py start         - Demarre l'agent")
        print("  python agent.py task <type>   - Execute une tache")
        print("")
        print("Exemples:")
        print("  python agent.py task start_n8n")
        print("  python agent.py task command 'docker ps'")
