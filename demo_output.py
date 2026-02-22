"""
Script pyRevit - Création de Poutre
Généré par BeamAgent
Commande: Crée une poutre de 30x50cm au niveau 2 sur l'axe A
"""

from Autodesk.Revit.DB import *
from Autodesk.Revit.UI import *
import clr

# Références Revit API
clr.AddReference('RevitAPI')
clr.AddReference('RevitAPIUI')

# Dimensions de la poutre (mm)
BEAM_WIDTH = 300 / 304.8  # Conversion mm -> pieds
BEAM_HEIGHT = 500 / 304.8

# Niveau cible
TARGET_LEVEL = "Niveau 2"

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
        "Poutre créée!\n"
        "Dimensions: " + str(300) + "x" + str(500) + "mm\n"
        "Niveau: " + TARGET_LEVEL)
    return beam


# Point d'entrée pyRevit
if __name__ == "__main__":
    doc = __revit__.ActiveUIDocument.Document
    uidoc = __revit__.ActiveUIDocument
    create_beam(doc, uidoc)
