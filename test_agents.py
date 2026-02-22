#!/usr/bin/env python3
"""
Test des agents BIM Revit
Lance ce script pour tester sans Revit
"""

import sys
from pathlib import Path

# Ajoute le dossier parent au path
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator import detect_agent, delegate_to_agent


def test_command(command: str):
    """Teste une commande"""
    print(f"\n{'='*60}")
    print(f"📝 Commande: {command}")
    print('='*60)
    
    agent, clean_cmd = detect_agent(command)
    
    if not agent:
        print("❌ Aucun agent détecté")
        return
    
    print(f"🤖 Agent: {agent}")
    
    result = delegate_to_agent(agent, clean_cmd)
    
    if result['success']:
        print(f"✅ Code généré ({len(result['code'])} caractères)")
        print(f"📊 Métadonnées: {result['metadata']}")
        
        # Sauvegarde le code dans un fichier
        output_file = Path(__file__).parent / f"output_{agent}.py"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(result['code'])
        print(f"💾 Code sauvegardé dans: {output_file}")
    else:
        print(f"❌ Erreur: {result['error']}")


def main():
    """Tests de démonstration"""
    
    print("🚀 Test des Agents BIM Revit")
    print("=" * 60)
    
    test_cases = [
        "Crée une poutre de 30x50cm au niveau 2 sur l'axe A",
        "Ajoute une colonne 40x40cm de 3m au niveau 1",
        "Fais un mur extérieur de 25cm d'épaisseur et 2.8m de haut",
        "Crée un toit à 30 degrés au niveau 3",
        "Dalle de 20cm structurelle au RDC",
    ]
    
    for test in test_cases:
        test_command(test)
    
    print(f"\n{'='*60}")
    print("✅ Tests terminés!")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
