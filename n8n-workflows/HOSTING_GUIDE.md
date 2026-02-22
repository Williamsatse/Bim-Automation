# Guide Hébergement n8n - 3 Méthodes

## Méthode 1 : Docker (Recommandé) ⭐

### Installation Docker

**Linux/Ubuntu :**
```bash
# Installe Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Ajoute ton user au groupe docker
sudo usermod -aG docker $USER

# Redémarre la session
newgrp docker
```

**Windows/Mac :**
1. Télécharge Docker Desktop : https://www.docker.com/products/docker-desktop
2. Installe et redémarre

### Lance n8n avec Docker

```bash
# Crée un dossier pour les données
mkdir -p ~/n8n-data

# Lance n8n
docker run -it --rm \
  --name n8n \
  -p 5678:5678 \
  -v ~/n8n-data:/home/node/.n8n \
  n8nio/n8n
```

**Accès :** http://localhost:5678

### Docker Compose (Production)

Crée `docker-compose.yml` :

```yaml
version: "3"

services:
  n8n:
    image: n8nio/n8n
    restart: always
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=ton_mot_de_passe
      - N8N_HOST=localhost
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=http://localhost:5678/
      - GENERIC_TIMEZONE=UTC
    volumes:
      - ~/.n8n:/home/node/.n8n
```

Lance avec :
```bash
docker-compose up -d
```

Arrête avec :
```bash
docker-compose down
```

---

## Méthode 2 : Cloud Gratuit (n8n Cloud)

### Option A : n8n Cloud Officiel

1. Va sur https://www.n8n.cloud
2. Crée un compte gratuit
3. **Limite :** 1 workflow actif, 100 exécutions/mois
4. Upgrade payant : $20/mois (illimité)

**Avantage :** Pas d'installation
**Inconvénient :** Limitations gratuites

### Option B : Railway.app (Recommandé gratuit)

1. Va sur https://railway.app
2. Connecte ton compte GitHub
3. Crée un nouveau projet
4. Clique **"Provision Template"** → Cherche "n8n"
5. Déploie !

**Limite :** $5/mois de crédit gratuit
**Coût réel :** Gratuit pour usage modéré

---

## Méthode 3 : VPS/Cloud (Production Pro)

### Option A : DigitalOcean ($5/mois)

```bash
# Crée un droplet Ubuntu 22.04
# SSH dans le serveur

# Met à jour
sudo apt update && sudo apt upgrade -y

# Installe Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# Crée le dossier n8n
mkdir -p ~/n8n && cd ~/n8n

# Crée docker-compose.yml
cat > docker-compose.yml << 'EOF'
version: "3"
services:
  n8n:
    image: n8nio/n8n:latest
    restart: always
    ports:
      - "5678:5678"
    environment:
      - N8N_BASIC_AUTH_ACTIVE=true
      - N8N_BASIC_AUTH_USER=admin
      - N8N_BASIC_AUTH_PASSWORD=CHANGEME
      - N8N_HOST=TON_IP
      - N8N_PORT=5678
      - N8N_PROTOCOL=http
      - WEBHOOK_URL=http://TON_IP:5678/
      - GENERIC_TIMEZONE=Europe/Paris
    volumes:
      - ~/.n8n:/home/node/.n8n
EOF

# Lance
docker-compose up -d

# Ouvre les ports firewall
sudo ufw allow 5678/tcp

# Vérifie que ça tourne
docker logs n8n
```

**Accès :** http://TON_IP:5678

### Option B : AWS EC2 (Free Tier)

1. Crée un compte AWS
2. Lance une instance EC2 (Ubuntu, Free Tier)
3. Configure le Security Group : Port 5678 ouvert
4. SSH et installe Docker (même commandes ci-dessus)

---

## 🌐 Exposer n8n à l'extérieur (Internet)

### Avec ngrok (Gratuit, testing)

```bash
# Installe ngrok
npm install -g ngrok

# Connecte ton compte (gratuit sur ngrok.com)
ngrok authtoken TON_TOKEN

# Expose n8n
ngrok http 5678
```

**Résultat :** URL publique type `https://abc123.ngrok.io`

### Avec Cloudflare Tunnel (Gratuit, permanent)

```bash
# Installe cloudflared
wget https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64
chmod +x cloudflared-linux-amd64
sudo mv cloudflared-linux-amd64 /usr/local/bin/cloudflared

# Authentifie
cloudflared tunnel login

# Crée un tunnel
cloudflared tunnel create n8n-tunnel

# Configure (crée ~/.cloudflared/config.yml)
cloudflared tunnel route dns n8n-tunnel n8n.ton-domain.com

# Lance
cloudflared tunnel run n8n-tunnel
```

---

## 🔒 Sécuriser n8n (Important !)

### Authentification Basique

Dans docker-compose.yml :
```yaml
environment:
  - N8N_BASIC_AUTH_ACTIVE=true
  - N8N_BASIC_AUTH_USER=admin
  - N8N_BASIC_AUTH_PASSWORD=MOT_DE_PASSE_FORT
```

### Avec Nginx + SSL (HTTPS)

```bash
# Installe nginx
sudo apt install nginx certbot python3-certbot-nginx -y

# Configure nginx
sudo nano /etc/nginx/sites-available/n8n
```

Contenu :
```nginx
server {
    listen 80;
    server_name n8n.ton-domain.com;

    location / {
        proxy_pass http://localhost:5678;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
    }
}
```

```bash
# Active
sudo ln -s /etc/nginx/sites-available/n8n /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx

# SSL
sudo certbot --nginx -d n8n.ton-domain.com
```

---

## ✅ Checklist Installation

### Docker local (pour tester)
- [ ] Docker installé
- [ ] Commande `docker run n8nio/n8n` exécutée
- [ ] Accès http://localhost:5678 fonctionne
- [ ] Workflow importé et testé

### Cloud (pour production)
- [ ] VPS créé (DigitalOcean/AWS/Railway)
- [ ] Docker installé sur le VPS
- [ ] Port 5678 ouvert dans le firewall
- [ ] n8n lancé avec docker-compose
- [ ] URL publique configurée (ngrok/Cloudflare)
- [ ] Authentification activée
- [ ] SSL/HTTPS configuré (optionnel mais recommandé)

---

## 🚀 Commandes Utiles

```bash
# Voir les logs
docker logs n8n -f

# Redémarrer
docker-compose restart

# Mettre à jour
docker-compose pull && docker-compose up -d

# Backup
tar czvf n8n-backup.tar.gz ~/.n8n

# Restore  
tar xzvf n8n-backup.tar.gz -C ~/
```

---

## ❓ Quelle méthode choisir ?

| Usage | Méthode | Coût |
|-------|---------|------|
| Test rapide | Docker local | Gratuit |
| Usage perso léger | Railway.app | Gratuit (~$5 crédit) |
| Usage perso régulier | DigitalOcean VPS | $5/mois |
| Professionnel | AWS/Cloud + n8n Cloud | $20-50/mois |

---

Tu veux que je détaille quelle méthode, Administrateur ?
- **1** = Docker local (test rapide)
- **2** = Railway (cloud gratuit)
- **3** = VPS DigitalOcean (production)