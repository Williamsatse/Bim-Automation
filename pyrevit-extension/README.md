# Extension pyRevit - BIM Agents

Extension pyRevit complète avec 5 boutons pour créer des éléments BIM.

## Structure

```
BIMAgents.extension/
├── extension.json                    # Configuration de l'extension
└── BIMAgents.tab/                    # Onglet dans Revit
    └── Elements.panel/               # Panneau "Éléments"
        ├── Beam.pushbutton/          # Bouton Poutre
        │   ├── script.py
        │   └── bundle.yaml
        ├── Column.pushbutton/        # Bouton Colonne
        ├── Wall.pushbutton/          # Bouton Mur
        ├── Roof.pushbutton/          # Bouton Toit
        └── Floor.pushbutton/         # Bouton Dalle
```

## Installation

### Méthode 1: Copie directe

1. **Trouve le dossier des extensions pyRevit** :
   ```
   %APPDATA%\pyRevit\Extensions
   ```
   Ou exécute dans pyRevit :
   ```python
   from pyrevit import script
   print(script.get_extensions_root())
   ```

2. **Copie le dossier** `BIMAgents.extension` dans ce dossier

3. **Redémarre Revit** ou recharge les extensions pyRevit

### Méthode 2: Installation via CLI pyRevit

```bash
# Clone le repo (si sur GitHub)
git clone https://github.com/ton-repo/revit-agents.git

# Installe l'extension
pyrevit extend ui BIMAgents --dest="C:\chemin\vers\BIMAgents.extension"
```

### Méthode 3: Dossier partagé (pour équipe)

1. **Place l'extension** sur un dossier réseau partagé
2. **Ajoute le chemin** dans pyRevit :
   - pyRevit → Settings → Add Extension Folder
   - Sélectionne le dossier parent de `BIMAgents.extension`

## Utilisation

### Dans Revit

1. **Ouvre l'onglet** "BIMAgents" dans le ruban Revit
2. **Clique** sur le bouton de l'élément voulu (Poutre, Colonne, etc.)
3. **Suis** les instructions dans les boîtes de dialogue
4. **Sélectionne** les points dans Revit pour placer l'élément

### Personnalisation

**Modifier les paramètres par défaut** :

Édite le fichier `script.py` dans chaque dossier `.pushbutton` :

```python
# Paramètres modifiables
BEAM_WIDTH_MM = 400      # Change ici
BEAM_HEIGHT_MM = 600     # Change ici
TARGET_LEVEL = "Niveau 2" # Change ici
```

## Dépannage

### Le bouton n'apparaît pas

1. Vérifie que le dossier s'appelle bien `BIMAgents.extension`
2. Vérifie `extension.json` est présent
3. Recharge pyRevit : pyRevit → Reload
4. Redémarre Revit

### Erreur "No module named 'Autodesk'"

C'est normal en dehors de Revit. Ces scripts ne fonctionnent **que** dans Revit avec pyRevit.

### Le type d'élément n'est pas trouvé

1. Vérifie que le projet contient des familles chargées
2. Pour les poutres : charge une famille "Structural Framing"
3. Pour les colonnes : charge une famille "Structural Column"

## Contribution

Pour ajouter un nouvel élément :

1. Crée un dossier `MonElement.pushbutton/`
2. Ajoute `script.py` et `bundle.yaml`
3. Teste dans Revit
4. Soumet une PR

## License

MIT License - Libre d'utilisation et modification.
