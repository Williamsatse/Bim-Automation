# OpenClaw Agent Autonome

Agent Python qui tourne en arrière-plan sur ton PC pour automatiser les tâches.

---

## 🚀 Démarrage Rapide (Windows)

```batch
# Double-clique sur control.bat
# Ou en ligne de commande:
control.bat start
```

## 🚀 Démarrage Rapide (Linux/Mac)

```bash
# Rendre exécutable
chmod +x control.sh

# Lancer
./control.sh
```

---

## 📋 Fonctionnalités

### Agent Principal (`agent.py`)
- ✅ Surveillance des services (Docker, n8n)
- ✅ Redémarrage automatique
- ✅ Exécution de commandes
- ✅ Journal des actions

### Scheduler (`scheduler.py`)
- ✅ Vérification Docker chaque minute
- ✅ Vérification n8n toutes les 5 minutes
- ✅ Sauvegarde quotidienne des workflows
- ✅ Surveillance de l'espace disque

---

## 🖥️ Interface de Contrôle

```
========================================
   OpenClaw Agent Controller
========================================

1. Démarrer l'agent
2. Arrêter l'agent
3. Vérifier le statut
4. Initialiser la config
5. Gestion n8n
6. Voir les logs
7. Démarrer le scheduler
8. Quitter
```

---

## 🐳 Gestion n8n

```
========================================
   Gestion n8n
========================================

1. Démarrer n8n  → Lance automatiquement n8n
2. Arrêter n8n    → Arrête le conteneur
3. Redémarrer n8n → Redémarre proprement
4. Voir les logs   → Affiche les logs en temps réel
5. Retour
```

---

## ⚙️ Utilisation Avancée

### Exécuter une tâche manuelle

```bash
python agent.py task start_n8n
python agent.py task command "docker ps"
python agent.py task check_services
```

### Créer des tâches personnalisées

Crée un fichier `tasks.json` :

```json
[
  {"type": "start_n8n"},
  {"type": "command", "command": "docker stats"},
  {"type": "check_services", "services": ["docker", "n8n"]}
]
```

L'agent les exécutera automatiquement.

---

## 📝 Logs

Les logs sont enregistrés dans :
- `agent.log` - Actions de l'agent
- `scheduler.log` - Tâches planifiées

---

## 🔧 Configuration

Le fichier `agent-config.json` est créé automatiquement :

```json
{
  "check_interval": 60,
  "notifications": true,
  "auto_restart": true,
  "services_to_monitor": ["docker", "n8n"]
}
```

Tu peux modifier ces valeurs selon tes besoins.

---

## 🎯 Scénarios d'Utilisation

### 1. Ton PC redémarre
- L'agent détecte que n8n ne tourne plus
- Il redémarre n8n automatiquement
- Tu reçois une notification

### 2. Sauvegarde automatique
- Tous les jours à 2h du matin
- Les workflows n8n sont sauvegardés
- Fichier : `~/n8n-backups/n8n-backup-YYYYMMDD.tar.gz`

### 3. Surveillance Docker
- Si Docker s'arrête → Alerte
- Si n8n crash → Redémarrage automatique

---

## 🔒 Sécurité

- L'agent ne demande jamais les mots de passe
- Il utilise les permissions de ton utilisateur
- Peut être arrêté à tout moment
- Logs transparents de toutes les actions

---

## 🆘 Dépannage

### Commandes utiles

```bash
# Vérifier si l'agent tourne
# Windows:
tasklist | findstr python

# Linux/Mac:
ps aux | grep agent.py

# Voir les logs n8n
docker logs n8n -f

# Redémarrer tout
./control.sh
# Puis choisir 3 (vérifier), 2 (arrêter), 1 (démarrer)
```

---

## 🔄 Intégration avec OpenClaw

L'agent peut être appelé via OpenClaw pour exécuter des tâches à distance :

```bash
# OpenClaw peut envoyer des commandes à l'agent
openclaw agent exec "start_n8n"
openclaw agent exec "docker ps"
```

---

Tu veux l'installer maintenant ?
1. Copie le dossier `openclaw-agent` sur ton PC
2. Double-clique sur `control.bat` (Windows) ou `./control.sh` (Linux)
3. Choisis **1** pour démarrer l'agent
4. Vérifie le statut avec **3**

