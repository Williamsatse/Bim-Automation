# Guide de Configuration - Automation WhatsApp-Telegram-OpenClaw

## Architecture du Workflow

```
WhatsApp Message → Webhook n8n → Formatage → Telegram + OpenClaw → Réponse
```

## Prérequis

1. **Instance n8n** en cours d'exécution
2. **Bot Telegram** créé via @BotFather
3. **OpenClaw** configuré avec webhook
4. **WhatsApp** (optionnel pour l'envoi)

## Étape 1 : Configuration Telegram

### Créer un bot Telegram

1. Message @BotFather sur Telegram
2. Envoie `/newbot`
3. Donne un nom : `WilliamsAssistant`
4. Donne un username : `WilliamsHIMBot` (doit finir par Bot)
5. **Copie le token** (ex: `123456789:ABCdefGHIjklMNOpqrSTUvwxyz`)

### Obtenir ton Chat ID

1. Envoie un message à ton bot
2. Visite : `https://api.telegram.org/botTON_TOKEN/getUpdates`
3. Cherche `"chat":{"id":12345678`
4. **Note ce nombre** (c'est ton Chat ID)

## Étape 2 : Configuration n8n

### 1. Importer le workflow

1. Ouvre n8n (http://localhost:5678)
2. Clique **"Add Workflow"**
3. Menu (⋮) → **Import from File**
4. Sélectionne `whatsapp-telegram-openclautomation.json`

### 2. Configurer les credentials

#### Credential Telegram
1. Ouvre le nœud "Forward to Telegram"
2. Clique sur l'icône **credential**
3. Sélectionne **"Create New Credential"**
4. Bot API Token : `TON_TOKEN_BOTFATHER`
5. Sauvegarde

#### Variables d'environnement
Dans n8n, va dans **Settings** → **Variables** :

| Variable | Valeur | Description |
|----------|--------|-------------|
| `TELEGRAM_CHAT_ID` | `12345678` | Ton Chat ID Telegram |
| `OPENCLAW_WEBHOOK_URL` | `http://localhost:18789/webhook` | URL webhook OpenClaw |

### 3. Configurer le webhook WhatsApp

Le webhook est déjà configuré dans le fichier :
- **URL** : `http://TON_IP:5678/webhook/whatsapp-webhook`
- **Méthode** : POST

## Étape 3 : Configuration OpenClaw

### Activer le webhook dans OpenClaw

Édite le fichier de config OpenClaw :

```bash
nano ~/.openclaw/config.yaml
```

Ajoute :

```yaml
webhooks:
  enabled: true
  port: 18789
  endpoints:
    - path: "/n8n-forward"
      action: "forward_to_telegram"
      target: "telegram:1327941907"
    - path: "/ai-process"
      action: "process_and_reply"
```

Redémarre OpenClaw :

```bash
openclaw gateway restart
```

## Étape 4 : Configuration WhatsApp (Optionnel)

Si tu veux recevoir des messages WhatsApp dans n8n :

### Méthode 1 : WhatsApp Business API (Pro)
- Nécessite Meta Business account
- Configuration complexe
- Pas recommandé pour usage perso

### Méthode 2 : WhatsApp Web + Webhook (Recommandé)
Utilise une solution comme :
- **whatsapp-web.js** (Node.js)
- **venom-bot** (Node.js)
- **yowsup** (Python)

Exemple avec whatsapp-web.js :

```javascript
// server.js
const qrcode = require('qrcode-terminal');
const { Client, LocalAuth } = require('whatsapp-web.js');
const client = new Client({
    authStrategy: new LocalAuth()
});

client.on('qr', qr => {
    qrcode.generate(qr, {small: true});
});

client.on('message_create', async msg => {
    // Forward to n8n
    await fetch('http://localhost:5678/webhook/whatsapp-webhook', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({
            sender: msg.from,
            message: msg.body,
            timestamp: new Date().toISOString()
        })
    });
});

client.initialize();
```

## Étape 5 : Tester le workflow

### Test 1 : Webhook n8n

```bash
curl -X POST http://localhost:5678/webhook/whatsapp-webhook \
  -H "Content-Type: application/json" \
  -d '{
    "sender": "+22587798225",
    "message": "Test message from WhatsApp",
    "timestamp": "2024-01-15T10:30:00Z"
  }'
```

### Test 2 : Vérifier Telegram

Tu dois recevoir un message sur Telegram avec :
- "📱 Nouveau message WhatsApp"
- Le numéro de l'expéditeur
- Le contenu du message

### Test 3 : OpenClaw Response

Si OpenClaw est configuré, il doit :
1. Recevoir le message
2. Le traiter (générer une réponse IA)
3. Renvoyer la réponse via n8n à Telegram

## Dépannage

### Le webhook ne répond pas

1. Vérifie que n8n tourne : `docker ps` ou `pm2 status`
2. Vérifie le port : `netstat -tlnp | grep 5678`
3. Teste avec curl (voir Test 1 ci-dessus)

### Pas de message Telegram

1. Vérifie le Bot Token (@BotFather)
2. Vérifie le Chat ID
3. Envoie `/start` à ton bot
4. Vérifie les logs n8n : `docker logs n8n` ou fichier logs

### OpenClaw ne répond pas

1. Vérifie le statut : `openclaw status`
2. Vérifie le webhook : `curl http://localhost:18789/webhook`
3. Vérifie les logs OpenClaw

## Utilisation Avancée

### Réponse automatique quand tu es offline

Tu peux modifier le workflow pour détecter si tu es en ligne :

```json
{
  "node": "Check User Status",
  "type": "n8n-nodes-base.if",
  "parameters": {
    "conditions": {
      "conditions": [
        {
          "leftValue": "={{ $json.user_status }}",
          "operator": {
            "type": "string",
            "operation": "equals"
          },
          "rightValue": "offline"
        }
      ]
    }
  }
}
```

Puis envoyer :
> "Salut c'est HIM, Williams n'est pas connecté en ce moment. Veuillez patienter un moment 😉"

## Fichiers Livrés

1. `whatsapp-telegram-openclautomation.json` - Workflow n8n complet
2. `SETUP_GUIDE.md` - Ce guide

## Support

Pour toute question :
- Documentation n8n : https://docs.n8n.io
- Forum OpenClaw : https://discord.com/invite/clawd
- API Telegram : https://core.telegram.org/bots/api
