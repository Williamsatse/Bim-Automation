#!/usr/bin/env python3
"""
Démonstration de l'intégration OpenClaw avec les Agents BIM
Ce fichier montre comment utiliser les agents depuis OpenClaw
"""

import sys
from pathlib import Path

# Ajoute le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator import detect_agent, delegate_to_agent


def demo_interactive():
    """Démonstration interactive"""
    
    print("=" * 70)
    print("🏗️  DÉMONSTRATION - Agents BIM pour Revit")
    print("=" * 70)
    print()
    print("Cette démo montre comment OpenClaw peut générer du code Python")
    print("pour créer des éléments BIM dans Revit via pyRevit.")
    print()
    
    # Exemples de commandes
    examples = [
        {
            "command": "Crée une poutre de 30x50cm au niveau 2 sur l'axe A",
            "description": "Poutre structurelle avec dimensions et placement"
        },
        {
            "command": "Ajoute une colonne carrée 40cm de 3m de haut au niveau 1",
            "description": "Colonne structurelle avec hauteur personnalisée"
        },
        {
            "command": "Fais un mur extérieur de 25cm d'épaisseur et 2.8m de haut",
            "description": "Mur avec épaisseur et hauteur"
        },
        {
            "command": "Crée un toit à 30 degrés au niveau 3",
            "description": "Toit en pente avec angle personnalisé"
        },
        {
            "command": "Dalle de 20cm structurelle au rez-de-chaussée",
            "description": "Dalle porteuse au RDC"
        },
    ]
    
    for i, example in enumerate(examples, 1):
        print(f"\n{'─' * 70}")
        print(f"📌 Exemple {i}/{len(examples)}")
        print(f"{'─' * 70}")
        print(f"💬 Commande: \"{example['command']}\"")
        print(f"📝 Description: {example['description']}")
        print()
        
        # Détecte l'agent
        agent, clean_cmd = detect_agent(example['command'])
        print(f"🤖 Agent détecté: {agent}")
        
        # Génère le code
        result = delegate_to_agent(agent, clean_cmd)
        
        if result['success']:
            print(f"✅ Code généré: {len(result['code'])} caractères")
            print(f"📊 Paramètres: {result['metadata']}")
            
            # Sauvegarde un exemple
            if i == 1:
                output_file = Path(__file__).parent / "demo_output.py"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(result['code'])
                print(f"💾 Exemple sauvegardé dans: {output_file}")
        else:
            print(f"❌ Erreur: {result['error']}")
    
    print(f"\n{'=' * 70}")
    print("✅ Démonstration terminée!")
    print(f"{'=' * 70}")
    print()
    print("Prochaines étapes:")
    print("1. Installe pyRevit: https://github.com/pyrevitlabs/pyRevit")
    print("2. Copie le dossier 'pyrevit-extension/BIMAgents.extension'")
    print("3. Redémarre Revit")
    print("4. Utilise les boutons dans l'onglet 'BIMAgents'")
    print()
    print("Ou demande-moi de générer du code personnalisé!")


if __name__ == "__main__":
    demo_interactive()
