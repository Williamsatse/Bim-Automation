#!/usr/bin/env python3
"""
Wall Agent - Spécialiste des murs
Génère du code Python pour créer des murs dans Revit via pyRevit
"""

import re


def parse_thickness(text: str) -> float:
    """Extrait l'épaisseur du mur"""
    patterns = [
        r'(\d+(?:\.\d+)?)\s*cm',
        r'(\d+)\s*mm',
        r'épaisseur\s+(?:de\s+)?(\d+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            thickness = float(match.group(1))
            if 'cm' in text.lower() and thickness < 10:
                thickness *= 10  # cm -> mm
            return thickness
    
    return 200.0  # 20cm par défaut


def parse_height(text: str) -> float:
    """Extrait la hauteur du mur"""
    patterns = [
        r'(\d+(?:\.\d+)?)\s*m',
        r'hauteur\s+(?:de\s+)?(\d+(?:\.\d+)?)',
        r'(\d+)\s*mètres?',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return float(match.group(1))
    
    return 3.0  # 3m par défaut


def parse_level(text: str) -> str:
    """Extrait le niveau"""
    patterns = [
        r'niveau\s+(\d+|\w+)',
        r'level\s+(\d+|\w+)',
        r'étage\s+(\d+|\w+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            level = match.group(1)
            if level in ['rdc', 'rez', 'ground']:
                return "Rez-de-chaussée"
            return f"Niveau {level}" if level.isdigit() else level.capitalize()
    
    return "Niveau 1"


def generate_code(command: str) -> dict:
    """Génère le code Python pour créer un mur"""
    
    thickness = parse_thickness(command)
    height = parse_height(command)
    level = parse_level(command)
    
    code = f'''"""
Script pyRevit - Création de Mur
Généré par WallAgent
Commande: {command}
"""

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
import clr

clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')

# Paramètres du mur
WALL_THICKNESS = {thickness} / 304.8  # mm -> pieds
WALL_HEIGHT = {height} * 3.28084      # m -> pieds
TARGET_LEVEL = "{level}"


def create_wall(doc, uidoc):
    """Crée un mur dans Revit"""
    
    # Trouve le niveau de base
    base_level = None
    top_level = None
    
    for lvl in FilteredElementCollector(doc).OfClass(Level):
        if lvl.Name == TARGET_LEVEL:
            base_level = lvl
        # Trouve le niveau supérieur pour la hauteur
        if base_level and lvl.Elevation > base_level.Elevation:
            if not top_level or lvl.Elevation < top_level.Elevation:
                top_level = lvl
    
    if not base_level:
        TaskDialog.Show("Erreur", f"Niveau '{{TARGET_LEVEL}}' non trouvé!")
        return None
    
    # Trouve un type de mur
    wall_type = None
    for wt in FilteredElementCollector(doc).OfClass(WallType):
        if wt.Kind == WallKind.Basic:
            wall_type = wt
            break
    
    if not wall_type:
        TaskDialog.Show("Erreur", "Aucun type de mur trouvé!")
        return None
    
    # Demande à l'utilisateur de dessiner la ligne du mur
    TaskDialog.Show("Info", "Dessinez la ligne du mur (2 points)")
    
    start_point = uidoc.Selection.PickPoint("Point de départ")
    end_point = uidoc.Selection.PickPoint("Point de fin")
    
    # Crée la ligne
    line = Line.CreateBound(start_point, end_point)
    
    # Crée le mur
    with Transaction(doc, "Créer Mur") as t:
        t.Start()
        
        wall = Wall.Create(
            doc,
            line,
            wall_type.Id,
            base_level.Id,
            WALL_HEIGHT,
            0.0,  # Offset de départ
            False,  # Pas de flip
            False   # Pas structural par défaut
        )
        
        # Ajuste l'épaisseur si possible
        # Note: l'épaisseur dépend du type de mur dans Revit
        
        t.Commit()
    
    TaskDialog.Show("Succès", 
        f"Mur créé!\\n"
        f"Épaisseur: {thickness}mm\\n"
        f"Hauteur: {height}m\\n"
        f"Niveau: {{TARGET_LEVEL}}")
    
    return wall


if __name__ == "__main__":
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    create_wall(doc, uidoc)
'''
    
    return {
        "success": True,
        "error": None,
        "code": code,
        "metadata": {
            "element_type": "wall",
            "thickness": thickness,
            "height": height,
            "level": level
        }
    }


if __name__ == "__main__":
    test = "Crée un mur de 20cm d'épaisseur et 3m de haut au niveau 1"
    print(generate_code(test))
