#!/usr/bin/env python3
"""
Exemple d'utilisation des agents BIM depuis ton code
"""

from orchestrator import detect_agent, delegate_to_agent


def example_1_simple():
    """Exemple simple: générer du code pour une poutre"""
    
    command = "Crée une poutre de 30x50cm au niveau 2 sur l'axe A"
    
    # Détecte quel agent est nécessaire
    agent, clean_command = detect_agent(command)
    print(f"Agent détecté: {agent}")
    
    # Génère le code
    result = delegate_to_agent(agent, clean_command)
    
    if result['success']:
        print("Code généré avec succès!")
        print(f"Métadonnées: {result['metadata']}")
        
        # Sauvegarde le code
        with open("output_beam.py", "w", encoding="utf-8") as f:
            f.write(result['code'])
        print("Code sauvegardé dans output_beam.py")


def example_2_batch():
    """Exemple batch: générer plusieurs éléments"""
    
    commands = [
        "Poutre 30x50cm niveau 1",
        "Colonne 40x40cm hauteur 3m niveau 1", 
        "Mur extérieur 25cm hauteur 2.8m",
        "Dalle 20cm structurelle RDC",
    ]
    
    for i, cmd in enumerate(commands):
        agent, _ = detect_agent(cmd)
        result = delegate_to_agent(agent, cmd)
        
        if result['success']:
            filename = f"output_{{i+1:02d}}_{{result['metadata']['element_type']}}.py"
            with open(filename, "w", encoding="utf-8") as f:
                f.write(result['code'])
            print(f"✅ {{filename}} généré")


def example_3_custom():
    """Exemple: créer ton propre agent"""
    
    # Tu peux créer un nouvel agent en copiant un existant
    # et en modifiant la logique de parsing et de génération
    
    print("""
Pour créer un nouvel agent:

1. Copie agents/beam_agent.py → agents/mon_agent.py
2. Modifie la fonction generate_code()
3. Ajoute le mapping dans orchestrator.py:
   "mon_element": "mon_agent"
4. Teste: python orchestrator.py "Crée un mon_element"
""")


if __name__ == "__main__":
    print("=" * 60)
    print("Exemples d'utilisation des Agents BIM")
    print("=" * 60)
    
    print("\n--- Exemple 1: Simple ---")
    example_1_simple()
    
    print("\n--- Exemple 2: Batch ---")
    example_2_batch()
    
    print("\n--- Exemple 3: Custom ---")
    example_3_custom()
