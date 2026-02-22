#!/usr/bin/env python3
"""
Beam Agent - Spécialiste des poutres
Génère du code Python pour créer des poutres dans Revit via pyRevit
"""

import re


def parse_dimensions(text: str) -> dict:
    """Extrait les dimensions d'une poutre du texte"""
    # Patterns communs: 30x50, 30x50cm, 300x500mm, etc.
    patterns = [
        r'(\d+)\s*x\s*(\d+)\s*(?:cm)?',  # 30x50 ou 30x50cm
        r'(\d+)\s*x\s*(\d+)\s*mm',       # 300x500mm
        r'(\d+)\s*cm\s*x\s*(\d+)\s*cm',  # 30cm x 50cm
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            width = int(match.group(1))
            height = int(match.group(2))
            
            # Convertir en mm si c'est en cm
            if 'cm' in text.lower() and width < 100:
                width *= 10
                height *= 10
            
            return {'width': width, 'height': height}
    
    # Valeurs par défaut
    return {'width': 300, 'height': 500}


def parse_level(text: str) -> str:
    """Extrait le niveau/étage du texte"""
    patterns = [
        r'niveau\s+(\d+|\w+)',
        r'level\s+(\d+|\w+)',
        r'étage\s+(\d+|\w+)',
        r'floor\s+(\d+|\w+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            level = match.group(1)
            return f"Niveau {level}" if level.isdigit() else level.capitalize()
    
    return "Niveau 1"  # Valeur par défaut


def parse_axis(text: str) -> str:
    """Extrait l'axe de placement"""
    patterns = [
        r'axe?\s*([A-Z]\d?)',
        r'axis\s*([A-Z]\d?)',
        r'sur\s*l?\s*\'?\s*axe?\s*([A-Z]\d?)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return match.group(1).upper()
    
    return None


def generate_code(command: str) -> dict:
    """Génère le code Python pour créer une poutre"""
    
    # Parse la commande
    dims = parse_dimensions(command)
    level = parse_level(command)
    axis = parse_axis(command)
    
    # Génère le code pyRevit
    code = f'''"""
Script pyRevit - Création de Poutre
Généré par BeamAgent
Commande: {command}
"""

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
import clr

# Références Revit API
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')

# Dimensions de la poutre (mm)
BEAM_WIDTH = {dims['width']} / 304.8  # Conversion mm -> pieds
BEAM_HEIGHT = {dims['height']} / 304.8

# Niveau cible
TARGET_LEVEL = "{level}"

# Fonction principale
def create_beam(doc, uidoc):
    """Crée une poutre dans Revit"""
    
    # Trouve le niveau
    level = None
    for lvl in FilteredElementCollector(doc).OfClass(Level):
        if lvl.Name == TARGET_LEVEL:
            level = lvl
            break
    
    if not level:
        TaskDialog.Show("Erreur", "Niveau '" + TARGET_LEVEL + "' non trouvé!")
        return None
    
    # Trouve un type de poutre (FamilySymbol)
    beam_type = None
    for fam in FilteredElementCollector(doc).OfClass(FamilySymbol):
        if fam.Category and fam.Category.Name == "Structural Framing":
            beam_type = fam
            break
    
    if not beam_type:
        TaskDialog.Show("Erreur", "Aucun type de poutre trouvé!")
        return None
    
    # Active le type si nécessaire
    if not beam_type.IsActive:
        beam_type.Activate()
        doc.Regenerate()
    
    # Demande à l'utilisateur de sélectionner deux points
    TaskDialog.Show("Info", "Sélectionnez le point de départ de la poutre")
    start_point = uidoc.Selection.PickPoint("Point de départ")
    
    TaskDialog.Show("Info", "Sélectionnez le point de fin de la poutre")
    end_point = uidoc.Selection.PickPoint("Point de fin")
    
    # Crée la ligne de la poutre
    line = Line.CreateBound(start_point, end_point)
    
    # Crée la poutre
    with Transaction(doc, "Créer Poutre") as t:
        t.Start()
        beam = doc.Create.NewFamilyInstance(line, beam_type, level, StructuralType.Beam)
        
        # Ajuste la hauteur (offset Z)
        offset = (BEAM_HEIGHT / 2) - (level.Elevation)
        beam.get_Parameter(BuiltInParameter.STRUCTURAL_BEAM_END0_ELEVATION).Set(offset)
        beam.get_Parameter(BuiltInParameter.STRUCTURAL_BEAM_END1_ELEVATION).Set(offset)
        
        t.Commit()
    
    TaskDialog.Show("Succès", 
        "Poutre créée!\\n"
        "Dimensions: " + str({dims['width']}) + "x" + str({dims['height']}) + "mm\\n"
        "Niveau: " + TARGET_LEVEL)
    return beam


# Point d'entrée pyRevit
if __name__ == "__main__":
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    create_beam(doc, uidoc)
'''
    
    return {
        "success": True,
        "error": None,
        "code": code,
        "metadata": {
            "element_type": "beam",
            "dimensions": dims,
            "level": level,
            "axis": axis
        }
    }


if __name__ == "__main__":
    # Test
    test_cmd = "Crée une poutre de 30x50cm au niveau 2 sur l'axe A"
    result = generate_code(test_cmd)
    print(result)
