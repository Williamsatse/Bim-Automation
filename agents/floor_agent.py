#!/usr/bin/env python3
"""
Floor Agent - Spécialiste des dalles
Génère du code Python pour créer des dalles dans Revit via pyRevit
"""

import re


def parse_thickness(text: str) -> float:
    """Extrait l'épaisseur de la dalle"""
    patterns = [
        r'(\d+(?:\.\d+)?)\s*cm',
        r'(\d+)\s*mm',
        r'épaisseur\s+(?:de\s+)?(\d+)',
        r'de\s+(\d+)\s*(?:cm|mm)?',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            thickness = float(match.group(1))
            if 'cm' in text.lower() and thickness < 10:
                thickness *= 10
            return thickness
    
    return 200.0  # 20cm par défaut


def parse_level(text: str) -> str:
    """Extrait le niveau"""
    patterns = [
        r'niveau\s+(\d+|\w+)',
        r'level\s+(\d+|\w+)',
        r'étage\s+(\d+|\w+)',
        r'sur\s+(\w+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            level = match.group(1)
            if level in ['rdc', 'rez', 'ground']:
                return "Rez-de-chaussée"
            return f"Niveau {level}" if level.isdigit() else level.capitalize()
    
    return "Niveau 1"


def parse_structural(text: str) -> bool:
    """Détecte si c'est une dalle structurelle"""
    structural_keywords = ['structurelle', 'structural', 'porteur', 'load-bearing']
    return any(kw in text.lower() for kw in structural_keywords)


def generate_code(command: str) -> dict:
    """Génère le code Python pour créer une dalle"""
    
    thickness = parse_thickness(command)
    level = parse_level(command)
    is_structural = parse_structural(command)
    
    code = f'''"""
Script pyRevit - Création de Dalle
Généré par FloorAgent
Commande: {command}
"""

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
import clr

clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')

# Paramètres de la dalle
FLOOR_THICKNESS = {thickness} / 304.8  # mm -> pieds
TARGET_LEVEL = "{level}"
IS_STRUCTURAL = {str(is_structural)}


def create_floor(doc, uidoc):
    """Crée une dalle dans Revit"""
    
    # Trouve le niveau
    level = None
    for lvl in FilteredElementCollector(doc).OfClass(Level):
        if lvl.Name == TARGET_LEVEL:
            level = lvl
            break
    
    if not level:
        TaskDialog.Show("Erreur", f"Niveau '{{TARGET_LEVEL}}' non trouvé!")
        return None
    
    # Trouve un type de dalle (FloorType)
    floor_type = None
    for ft in FilteredElementCollector(doc).OfClass(FloorType):
        floor_type = ft
        break
    
    if not floor_type:
        TaskDialog.Show("Erreur", "Aucun type de dalle trouvé!")
        return None
    
    # Demande à l'utilisateur de dessiner le contour
    TaskDialog.Show("Info", "Sélectionnez les points du contour de la dalle (clic droit pour terminer)")
    
    points = []
    while True:
        try:
            point = uidoc.Selection.PickPoint("Point suivant (ESC pour terminer)")
            # Projecte sur le niveau
            projected = XYZ(point.X, point.Y, level.Elevation)
            points.append(projected)
        except:
            break
    
    if len(points) < 3:
        TaskDialog.Show("Erreur", "Il faut au moins 3 points pour créer une dalle!")
        return None
    
    # Crée la courbe du contour
    curve_array = CurveArray()
    for i in range(len(points)):
        start = points[i]
        end = points[(i + 1) % len(points)]
        line = Line.CreateBound(start, end)
        curve_array.Append(line)
    
    curve_loop = CurveLoop()
    for curve in curve_array:
        curve_loop.Append(curve)
    
    # Crée la dalle
    with Transaction(doc, "Créer Dalle") as t:
        t.Start()
        
        # Utilise Floor.Create pour les versions récentes de Revit
        # ou NewFloor pour les anciennes
        try:
            floor = Floor.Create(
                doc,
                [curve_loop],
                floor_type.Id,
                level.Id
            )
        except:
            # Méthode legacy
            floor = doc.Create.NewFloor(
                curve_array,
                floor_type,
                level,
                False  # Pas structural par défaut
            )
        
        # Marque comme structurel si demandé
        if IS_STRUCTURAL and floor:
            param = floor.get_Parameter(BuiltInParameter.FLOOR_PARAM_IS_STRUCTURAL)
            if param:
                param.Set(True)
        
        t.Commit()
    
    TaskDialog.Show("Succès", 
        f"Dalle créée!\\n"
        f"Épaisseur: {thickness}mm\\n"
        f"Niveau: {{TARGET_LEVEL}}\\n"
        f"Structurelle: {{'Oui' if IS_STRUCTURAL else 'Non'}}")
    
    return floor


if __name__ == "__main__":
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    create_floor(doc, uidoc)
'''
    
    return {
        "success": True,
        "error": None,
        "code": code,
        "metadata": {
            "element_type": "floor",
            "thickness": thickness,
            "level": level,
            "structural": is_structural
        }
    }


if __name__ == "__main__":
    test = "Crée une dalle de 25cm au niveau 1"
    print(generate_code(test))
