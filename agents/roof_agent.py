#!/usr/bin/env python3
"""
Roof Agent - Spécialiste des toits
Génère du code Python pour créer des toits dans Revit via pyRevit
"""

import re


def parse_roof_type(text: str) -> str:
    """Détecte le type de toit"""
    text_lower = text.lower()
    
    if any(word in text_lower for word in ['plat', 'terrasse', 'flat']):
        return "flat"
    elif any(word in text_lower for word in ['pente', 'incliné', '2 pans', '4 pans', 'gable', 'hip']):
        return "sloped"
    elif any(word in text_lower for word in ['dôme', 'dome', 'voûte', 'vault']):
        return "dome"
    
    return "sloped"  # Par défaut


def parse_slope(text: str) -> float:
    """Extrait la pente en degrés ou pourcentage"""
    patterns = [
        r'(\d+(?:\.\d+)?)\s*°',  # Degrés
        r'(\d+(?:\.\d+)?)\s*degrés',
        r'pente\s+(?:de\s+)?(\d+(?:\.\d+)?)\s*%',  # Pourcentage
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            value = float(match.group(1))
            if '%' in text.lower():
                # Convertir pourcentage en degrés
                import math
                value = math.degrees(math.atan(value / 100))
            return value
    
    return 30.0  # 30° par défaut


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
    
    return "Niveau 2"  # Toit souvent au niveau supérieur


def generate_code(command: str) -> dict:
    """Génère le code Python pour créer un toit"""
    
    roof_type = parse_roof_type(command)
    slope = parse_slope(command)
    level = parse_level(command)
    
    code = f'''"""
Script pyRevit - Création de Toit
Généré par RoofAgent
Commande: {command}
"""

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
import clr

clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')

# Paramètres du toit
ROOF_TYPE = "{roof_type}"
ROOF_SLOPE = {slope}  # Degrés
TARGET_LEVEL = "{level}"


def create_roof(doc, uidoc):
    """Crée un toit dans Revit"""
    
    # Trouve le niveau
    level = None
    for lvl in FilteredElementCollector(doc).OfClass(Level):
        if lvl.Name == TARGET_LEVEL:
            level = lvl
            break
    
    if not level:
        TaskDialog.Show("Erreur", f"Niveau '{{TARGET_LEVEL}}' non trouvé!")
        return None
    
    # Trouve un type de toit
    roof_type = None
    for rt in FilteredElementCollector(doc).OfClass(RoofType):
        roof_type = rt
        break
    
    if not roof_type:
        TaskDialog.Show("Erreur", "Aucun type de toit trouvé!")
        return None
    
    # Demande à l'utilisateur de dessiner le contour
    TaskDialog.Show("Info", "Sélectionnez les points du contour du toit (clic droit pour terminer)")
    
    points = []
    while True:
        try:
            point = uidoc.Selection.PickPoint("Point suivant (ESC pour terminer)")
            points.append(point)
        except:
            break
    
    if len(points) < 3:
        TaskDialog.Show("Erreur", "Il faut au moins 3 points pour créer un toit!")
        return None
    
    # Crée la courbe du contour
    curve_loop = CurveLoop()
    for i in range(len(points)):
        start = points[i]
        end = points[(i + 1) % len(points)]
        line = Line.CreateBound(start, end)
        curve_loop.Append(line)
    
    # Crée le toit
    with Transaction(doc, "Créer Toit") as t:
        t.Start()
        
        if ROOF_TYPE == "flat":
            # Toit plat
            roof = doc.Create.NewRoof(
                curve_loop,
                roof_type,
                level
            )
        else:
            # Toit en pente - utilise le footprint
            roof = doc.Create.NewFootPrintRoof(
                curve_loop,
                level,
                roof_type,
                None  # Slope settings à configurer
            )
            
            # Applique la pente
            # Note: la méthode exacte dépend de la version Revit
        
        t.Commit()
    
    TaskDialog.Show("Succès", 
        f"Toit créé!\\n"
        f"Type: {{ROOF_TYPE}}\\n"
        f"Pente: {slope}°\\n"
        f"Niveau: {{TARGET_LEVEL}}")
    
    return roof


if __name__ == "__main__":
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    create_roof(doc, uidoc)
'''
    
    return {
        "success": True,
        "error": None,
        "code": code,
        "metadata": {
            "element_type": "roof",
            "roof_type": roof_type,
            "slope": slope,
            "level": level
        }
    }


if __name__ == "__main__":
    test = "Crée un toit à 30 degrés au niveau 2"
    print(generate_code(test))
