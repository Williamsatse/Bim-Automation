# Configuration OpenClaw - Revit BIM Agents

## Description
Système multi-agents pour la création d'éléments BIM dans Revit via pyRevit.

## Agents

### Orchestrator
- **Fichier**: `orchestrator.py`
- **Rôle**: Analyse la commande et délègue au bon agent
- **Entrée**: Commande en langage naturel
- **Sortie**: Code Python pyRevit

### BeamAgent
- **Fichier**: `agents/beam_agent.py`
- **Spécialité**: Poutres structurelles
- **Paramètres**: largeur, hauteur, niveau, axe

### ColumnAgent
- **Fichier**: `agents/column_agent.py`
- **Spécialité**: Colonnes structurelles
- **Paramètres**: section (carrée/rectangulaire), hauteur, niveau

### WallAgent
- **Fichier**: `agents/wall_agent.py`
- **Spécialité**: Murs
- **Paramètres**: épaisseur, hauteur, niveau, type

### RoofAgent
- **Fichier**: `agents/roof_agent.py`
- **Spécialité**: Toits
- **Paramètres**: type (plat/incliné), pente, niveau

### FloorAgent
- **Fichier**: `agents/floor_agent.py`
- **Spécialité**: Dalles
- **Paramètres**: épaisseur, niveau, structural/non-structural

## Utilisation

```python
# Exemple d'appel depuis OpenClaw
from revit_agents.orchestrator import generate_element

code = generate_element("Crée une poutre 30x50cm au niveau 2")
# Retourne le code Python pyRevit
```

## Dépendances
- pyRevit installé dans Revit
- Revit 2018+ (pour compatibilité API)
- Familles de base disponibles dans le projet

## Notes
- Les agents génèrent du code Python exécutable dans pyRevit
- L'utilisateur doit sélectionner les points dans Revit
- Les types de familles doivent exister dans le projet
