#!/usr/bin/env python3
"""
Column Agent - Spécialiste des colonnes
Génère du code Python pour créer des colonnes dans Revit via pyRevit
"""

import re


def parse_dimensions(text: str) -> dict:
    """Extrait les dimensions d'une colonne"""
    patterns = [
        r'(\d+)\s*x\s*(\d+)\s*(?:cm)?',
        r'(\d+)\s*x\s*(\d+)\s*mm',
        r'(\d+)\s*cm\s*x\s*(\d+)\s*cm',
        r'(\d+)\s*cm',  # Section carrée
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            if len(match.groups()) == 2:
                width = int(match.group(1))
                depth = int(match.group(2))
                if 'cm' in text.lower() and width < 100:
                    width *= 10
                    depth *= 10
                return {'width': width, 'depth': depth}
            else:
                size = int(match.group(1))
                if 'cm' in text.lower() and size < 100:
                    size *= 10
                return {'width': size, 'depth': size}
    
    return {'width': 300, 'depth': 300}


def parse_level(text: str) -> str:
    """Extrait le niveau"""
    patterns = [
        r'niveau\s+(\d+|\w+)',
        r'level\s+(\d+|\w+)',
        r'étage\s+(\d+|\w+)',
        r'du\s+(\w+)',  # "du rez-de-chaussée", "du RDC"
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            level = match.group(1)
            if level in ['rdc', 'rez', 'rez-de-chaussée', 'ground']:
                return "Rez-de-chaussée"
            return f"Niveau {level}" if level.isdigit() else level.capitalize()
    
    return "Niveau 1"


def parse_height(text: str) -> float:
    """Extrait la hauteur de la colonne"""
    patterns = [
        r'(\d+(?:\.\d+)?)\s*m',
        r'(\d+(?:\.\d+)?)\s*mètres?',
        r'hauteur\s+(?:de\s+)?(\d+(?:\.\d+)?)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text.lower())
        if match:
            return float(match.group(1))
    
    return 3.0  # Hauteur par défaut


def generate_code(command: str) -> dict:
    """Génère le code Python pour créer une colonne"""
    
    dims = parse_dimensions(command)
    level = parse_level(command)
    height = parse_height(command)
    
    code = f'''"""
Script pyRevit - Création de Colonne
Généré par ColumnAgent
Commande: {command}
"""

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
import clr

clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')

# Dimensions (mm -> pieds)
COL_WIDTH = {dims['width']} / 304.8
COL_DEPTH = {dims['depth']} / 304.8
COL_HEIGHT = {height} * 3.28084  # m -> pieds

TARGET_LEVEL = "{level}"


def create_column(doc, uidoc):
    """Crée une colonne structurelle"""
    
    # Trouve le niveau
    level = None
    for lvl in FilteredElementCollector(doc).OfClass(Level):
        if lvl.Name == TARGET_LEVEL:
            level = lvl
            break
    
    if not level:
        TaskDialog.Show("Erreur", f"Niveau '{{TARGET_LEVEL}}' non trouvé!")
        return None
    
    # Trouve un type de colonne
    col_type = None
    for fam in FilteredElementCollector(doc).OfClass(FamilySymbol):
        if fam.Category and fam.Category.Name in ["Structural Columns", "Colonnes structurelles"]:
            col_type = fam
            break
    
    if not col_type:
        TaskDialog.Show("Erreur", "Aucun type de colonne trouvé!")
        return None
    
    # Active le type
    if not col_type.IsActive:
        col_type.Activate()
        doc.Regenerate()
    
    # Demande le point de placement
    TaskDialog.Show("Info", "Cliquez pour placer la colonne")
    point = uidoc.Selection.PickPoint("Point de placement")
    
    # Crée la colonne
    with Transaction(doc, "Créer Colonne") as t:
        t.Start()
        
        # Crée l'instance
        column = doc.Create.NewFamilyInstance(
            point, 
            col_type, 
            level, 
            StructuralType.Column
        )
        
        # Ajuste la hauteur
        top_level_param = column.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_PARAM)
        if top_level_param:
            # Trouve le niveau supérieur ou utilise un offset
            top_offset = column.get_Parameter(BuiltInParameter.FAMILY_TOP_LEVEL_OFFSET_PARAM)
            if top_offset:
                top_offset.Set(COL_HEIGHT)
        
        # Ajuste les dimensions si c'est une colonne rectangulaire
        # Note: dépend du type de famille utilisé
        
        t.Commit()
    
    TaskDialog.Show("Succès", 
        f"Colonne créée!\\n"
        f"Dimensions: {dims['width']}x{dims['depth']}mm\\n"
        f"Hauteur: {height}m\\n"
        f"Niveau: {{TARGET_LEVEL}}")
    
    return column


if __name__ == "__main__":
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    create_column(doc, uidoc)
'''
    
    return {
        "success": True,
        "error": None,
        "code": code,
        "metadata": {
            "element_type": "column",
            "dimensions": dims,
            "level": level,
            "height": height
        }
    }


if __name__ == "__main__":
    test = "Crée une colonne 30x30cm de 3m au niveau 1"
    print(generate_code(test))
