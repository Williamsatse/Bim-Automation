#!/usr/bin/env python3
"""
Revit BIM Orchestrator
Délègue les commandes aux agents spécialisés
"""

import json
import sys
from pathlib import Path

# Mapping des agents
AGENTS = {
    "poutre": "beam_agent",
    "poutres": "beam_agent",
    "beam": "beam_agent",
    "beams": "beam_agent",
    "colonne": "column_agent",
    "colonnes": "column_agent",
    "column": "column_agent",
    "columns": "column_agent",
    "mur": "wall_agent",
    "murs": "wall_agent",
    "wall": "wall_agent",
    "walls": "wall_agent",
    "toit": "roof_agent",
    "toits": "roof_agent",
    "roof": "roof_agent",
    "roofs": "roof_agent",
    "dalle": "floor_agent",
    "dalles": "floor_agent",
    "floor": "floor_agent",
    "floors": "floor_agent",
    "slab": "floor_agent",
    "slabs": "floor_agent",
}


def detect_agent(command: str) -> tuple[str, str]:
    """Détecte quel agent est nécessaire et nettoie la commande"""
    command_lower = command.lower()
    
    for keyword, agent in AGENTS.items():
        if keyword in command_lower:
            return agent, command
    
    return None, command


def delegate_to_agent(agent_name: str, command: str) -> dict:
    """Appelle l'agent spécialisé"""
    agent_path = Path(__file__).parent / f"agents/{agent_name}.py"
    
    if not agent_path.exists():
        return {
            "success": False,
            "error": f"Agent '{agent_name}' non trouvé",
            "code": None
        }
    
    # Import dynamique de l'agent
    import importlib.util
    spec = importlib.util.spec_from_file_location(agent_name, agent_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    # Appelle la fonction generate_code de l'agent
    if hasattr(module, 'generate_code'):
        return module.generate_code(command)
    else:
        return {
            "success": False,
            "error": f"Agent '{agent_name}' n'a pas de fonction generate_code",
            "code": None
        }


def main():
    """Point d'entrée principal"""
    if len(sys.argv) < 2:
        print("Usage: python orchestrator.py 'commande'")
        print("Exemple: python orchestrator.py 'Crée une poutre de 30x50cm sur l'axe A'")
        sys.exit(1)
    
    command = ' '.join(sys.argv[1:])
    
    print(f"🎯 Commande reçue: {command}")
    print()
    
    # Détecte l'agent
    agent, clean_command = detect_agent(command)
    
    if not agent:
        print("❌ Je n'ai pas compris quel élément BIM tu veux créer.")
        print("Essaye avec: poutre, colonne, mur, toit, dalle")
        sys.exit(1)
    
    print(f"🤖 Agent détecté: {agent}")
    print()
    
    # Délègue à l'agent
    result = delegate_to_agent(agent, clean_command)
    
    if result['success']:
        print("✅ Code généré avec succès!")
        print()
        print("=" * 60)
        print("CODE PYTHON POUR PYREVIT:")
        print("=" * 60)
        print()
        print(result['code'])
        print()
        print("=" * 60)
        print()
        print("📋 Instructions:")
        print("1. Copie ce code dans un fichier .py")
        print("2. Place-le dans le dossier pyRevit/extensions")
        print("3. Exécute depuis Revit")
    else:
        print(f"❌ Erreur: {result['error']}")
        sys.exit(1)


if __name__ == '__main__':
    main()
