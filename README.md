# Revit BIM Agents 🤖

Système multi-agents pour créer des éléments BIM dans Revit via pyRevit.

## Architecture

```
Toi (Telegram/Web) → Orchestrator → Agent Spécialisé → Code Python → pyRevit → Revit
```

## Agents Disponibles

| Agent | Élément | Compétences |
|-------|---------|-------------|
| `beam_agent` | Poutres | Dimensions, placement, alignement |
| `column_agent` | Colonnes | Section, hauteur, placement |
| `wall_agent` | Murs | Épaisseur, hauteur, niveau |
| `roof_agent` | Toits | Pente, type (plat/incliné), contour |
| `floor_agent` | Dalles | Épaisseur, structural/non-structural |

## Utilisation

### 1. Ligne de commande

```bash
python orchestrator.py "Crée une poutre de 30x50cm au niveau 2"
```

### 2. Depuis OpenClaw

Demande-moi simplement :
- *"Crée une colonne 30x30cm de 3m au niveau 1"*
- *"Ajoute un mur de 20cm sur l'axe A"*
- *"Fais une dalle de 25cm au RDC"*

## Installation dans Revit

1. **Installer pyRevit** : https://github.com/pyrevitlabs/pyRevit

2. **Copier les scripts** :
   ```
   %APPDATA%/pyRevit/Extensions/MyExtension.extension/
   ```

3. **Créer un fichier `.pushbutton`** pour chaque script

4. **Structure** :
   ```
   MyExtension.extension/
   └── MyTab.tab/
       └── BIM Agents.panel/
           ├── Poutre.pushbutton/
           │   ├── script.py
           │   └── icon.png
           ├── Colonne.pushbutton/
           │   └── script.py
           └── ...
   ```

## Format des Commandes

Les agents comprennent le langage naturel. Exemples :

```
"Poutre 30x50cm niveau 2 axe A"
"Colonne carrée 40cm hauteur 3m niveau 1"
"Mur extérieur 25cm hauteur 2.5m"
"Toit à 30 degrés niveau 3"
"Dalle 20cm structurelle RDC"
```

## Personnalisation

### Ajouter un nouvel agent

1. Créer `agents/new_agent.py`
2. Implémenter `generate_code(command: str) -> dict`
3. Ajouter le mapping dans `orchestrator.py`

### Modifier les valeurs par défaut

Éditer les fonctions `parse_*()` dans chaque agent.

## Limitations Actuelles

- Nécessite pyRevit installé
- L'utilisateur doit sélectionner les points dans Revit
- Les types de familles doivent exister dans le projet
- Pas de vérification de collision (clash detection)

## Roadmap

- [ ] Intégration avec les familles paramétriques
- [ ] Génération automatique de contours (IA)
- [ ] Vérification de conformité normative
- [ ] Export vers d'autres formats (IFC, DWG)
- [ ] Interface web pour visualiser avant/après

---

*Généré par OpenClaw BIM Agents*
