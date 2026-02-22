#!/usr/bin/env python3
"""
OpenClaw Scheduler
Planifie et execute des taches automatiques
"""

import schedule
import time
import json
from datetime import datetime
from pathlib import Path
import subprocess

AGENT_DIR = Path(__file__).parent
SCHEDULE_FILE = AGENT_DIR / "schedule.json"
LOG_FILE = AGENT_DIR / "scheduler.log"


def log(message):
    """Log un message"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {message}"
    print(log_entry)
    with open(LOG_FILE, 'a') as f:
        f.write(log_entry + "\n")


def execute_command(command):
    """Execute une commande"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=60
        )
        return result.returncode == 0, result.stdout, result.stderr
    except Exception as e:
        return False, "", str(e)


def docker_status_check():
    """Verifie le statut de Docker"""
    log("Verification Docker...")
    success, stdout, stderr = execute_command("docker ps")
    if success:
        log("Docker OK")
    else:
        log(f"ERREUR Docker: {stderr}")


def n8n_status_check():
    """Verifie si n8n tourne"""
    log("Verification n8n...")
    success, stdout, _ = execute_command("docker ps -q -f name=n8n")
    if stdout.strip():
        log("n8n OK")
    else:
        log("n8n ARRETE - Redemarrage...")
        execute_command("docker run -d --name n8n -p 5678:5678 -v ~/.n8n:/home/node/.n8n n8nio/n8n")


def backup_n8n():
    """Sauvegarde les workflows n8n"""
    log("Sauvegarde n8n...")
    backup_dir = Path.home() / "n8n-backups"
    backup_dir.mkdir(exist_ok=True)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = backup_dir / f"n8n-backup-{timestamp}.tar.gz"
    
    cmd = f"tar czf {backup_file} ~/.n8n"
    success, _, stderr = execute_command(cmd)
    
    if success:
        log(f"Sauvegarde creee: {backup_file}")
    else:
        log(f"Erreur sauvegarde: {stderr}")


def check_disk_space():
    """Verifie l'espace disque"""
    log("Verification espace disque...")
    success, stdout, _ = execute_command("df -h / | tail -1 | awk '{print $5}'")
    if success:
        usage = stdout.strip()
        log(f"Usage disque: {usage}")
        
        # Alerte si > 90%
        if int(usage.replace('%', '')) > 90:
            log("ALERTE: Espace disque faible!")


def load_schedule():
    """Charge les taches planifiees"""
    if SCHEDULE_FILE.exists():
        with open(SCHEDULE_FILE, 'r') as f:
            return json.load(f)
    return {}


def setup_default_schedule():
    """Configure les taches par defaut"""
    log("Configuration des taches planifiees...")
    
    # Toutes les minutes: verifie Docker
    schedule.every(1).minutes.do(docker_status_check)
    
    # Toutes les 5 minutes: verifie n8n
    schedule.every(5).minutes.do(n8n_status_check)
    
    # Toutes les heures: verifie l'espace disque
    schedule.every(1).hours.do(check_disk_space)
    
    # Tous les jours a 2h du matin: sauvegarde
    schedule.every().day.at("02:00").do(backup_n8n)
    
    log("Taches configurees:")
    log("- Docker check: chaque minute")
    log("- n8n check: toutes les 5 minutes")
    log("- Disk check: chaque heure")
    log("- Backup: tous les jours a 2h")


def run_scheduler():
    """Boucle principale du scheduler"""
    log("=" * 50)
    log("OpenClaw Scheduler demarre")
    log("=" * 50)
    
    setup_default_schedule()
    
    while True:
        try:
            schedule.run_pending()
            time.sleep(1)
        except Exception as e:
            log(f"Erreur scheduler: {e}")
            time.sleep(5)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1:
        if sys.argv[1] == "once":
            # Execute une fois tous les checks
            docker_status_check()
            n8n_status_check()
            check_disk_space()
        elif sys.argv[1] == "backup":
            backup_n8n()
        elif sys.argv[1] == "start":
            run_scheduler()
    else:
        print("OpenClaw Scheduler")
        print("")
        print("Usage:")
        print("  python scheduler.py start    - Demarre le scheduler")
        print("  python scheduler.py once     - Execute une fois")
        print("  python scheduler.py backup   - Sauvegarde immediate")
