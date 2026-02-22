#!/usr/bin/env python3
"""
Skill OpenClaw pour les Agents BIM Revit
Permet d'appeler les agents depuis les conversations
"""

import sys
from pathlib import Path

# Ajoute le dossier revit-agents au path
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator import detect_agent, delegate_to_agent


def generate_revit_element(command: str) -> str:
    """
    Génère du code Python pyRevit pour créer un élément BIM dans Revit.
    
    Args:
        command: Description de l'élément à créer (ex: "poutre 30x50cm niveau 2")
    
    Returns:
        Code Python prêt à exécuter dans pyRevit
    """
    
    # Détecte l'agent
    agent, clean_cmd = detect_agent(command)
    
    if not agent:
        return """❌ Je n'ai pas compris quel élément tu veux créer.

Éléments supportés:
• Poutres (beam, poutre)
• Colonnes (column, colonne)  
• Murs (wall, mur)
• Toits (roof, toit)
• Dalles (floor, dalle, slab)

Exemple: "Crée une poutre de 30x50cm au niveau 2""""
    
    # Génère le code
    result = delegate_to_agent(agent, clean_cmd)
    
    if not result['success']:
        return f"❌ Erreur lors de la génération: {result['error']}"
    
    # Retourne le code formaté
    response = f"""✅ Code généré par **{agent.replace('_', ' ').title()}**

📊 **Paramètres détectés:**
"""
    
    for key, value in result['metadata'].items():
        response += f"• {key}: {value}\n"
    
    response += f"""
📋 **Code Python pour pyRevit:**

```python
{result['code']}
```

💾 **Instructions:**
1. Copie ce code dans un fichier `.py`
2. Place-le dans `pyRevit/extensions/.../`
3. Exécute depuis Revit
"""
    
    return response


# Fonction pour OpenClaw
def handle_command(command: str) -> str:
    """Point d'entrée pour OpenClaw"""
    return generate_revit_element(command)


if __name__ == "__main__":
    # Test
    if len(sys.argv) > 1:
        cmd = ' '.join(sys.argv[1:])
        print(handle_command(cmd))
    else:
        # Test par défaut
        print(handle_command("Crée une poutre de 30x50cm au niveau 2"))
