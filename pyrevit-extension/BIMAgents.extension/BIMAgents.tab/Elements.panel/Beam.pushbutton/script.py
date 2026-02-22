# -*- coding: utf-8 -*-
"""
BIM Agent - Création de Poutre
Génère et exécute une poutre structurelle
"""

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
import clr

clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')

# Paramètres modifiables
BEAM_WIDTH_MM = 300      # Largeur en mm
BEAM_HEIGHT_MM = 500     # Hauteur en mm
TARGET_LEVEL = "Niveau 1"  # Niveau de placement

# Conversion mm -> pieds (unités Revit)
BEAM_WIDTH = BEAM_WIDTH_MM / 304.8
BEAM_HEIGHT = BEAM_HEIGHT_MM / 304.8


def create_beam(doc, uidoc):
    """Crée une poutre structurelle"""
    
    # Trouve le niveau
    level = None
    for lvl in FilteredElementCollector(doc).OfClass(Level):
        if lvl.Name == TARGET_LEVEL:
            level = lvl
            break
    
    if not level:
        TaskDialog.Show("Erreur", "Niveau '" + TARGET_LEVEL + "' non trouvé!")
        return None
    
    # Trouve un type de poutre
    beam_type = None
    for fam in FilteredElementCollector(doc).OfClass(FamilySymbol):
        if fam.Category and fam.Category.Name == "Structural Framing":
            beam_type = fam
            break
    
    if not beam_type:
        TaskDialog.Show("Erreur", "Aucun type de poutre trouvé!")
        return None
    
    # Active le type
    if not beam_type.IsActive:
        beam_type.Activate()
        doc.Regenerate()
    
    # Demande les points
    TaskDialog.Show("Info", "Sélectionnez le point de départ de la poutre")
    start_point = uidoc.Selection.PickPoint("Point de départ")
    
    TaskDialog.Show("Info", "Sélectionnez le point de fin de la poutre")
    end_point = uidoc.Selection.PickPoint("Point de fin")
    
    # Crée la ligne
    line = Line.CreateBound(start_point, end_point)
    
    # Crée la poutre
    with Transaction(doc, "Créer Poutre") as t:
        t.Start()
        beam = doc.Create.NewFamilyInstance(line, beam_type, level, StructuralType.Beam)
        
        # Ajuste la hauteur
        offset = (BEAM_HEIGHT / 2) - (level.Elevation)
        beam.get_Parameter(BuiltInParameter.STRUCTURAL_BEAM_END0_ELEVATION).Set(offset)
        beam.get_Parameter(BuiltInParameter.STRUCTURAL_BEAM_END1_ELEVATION).Set(offset)
        
        t.Commit()
    
    TaskDialog.Show("Succès", 
        "Poutre créée!\\n"
        "Dimensions: " + str(BEAM_WIDTH_MM) + "x" + str(BEAM_HEIGHT_MM) + "mm\\n"
        "Niveau: " + TARGET_LEVEL)
    
    return beam


# Point d'entrée pyRevit
if __name__ == "__main__":
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    create_beam(doc, uidoc)
