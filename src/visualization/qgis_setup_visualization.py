import os
from qgis.core import QgsVectorLayer, QgsProject, QgsCategorizedSymbolRenderer, QgsRendererCategory, QgsSymbol, QgsMarkerSymbol

# File paths (absolute)
project_root = r'D:\Research_AI\Brandenburg_groundwater'
wells_path = os.path.join(project_root, 'data', 'processed', 'topmost_wells_viz.gpkg')
shp_path = os.path.join(project_root, 'data', 'raw', 'Groundwater_distance', 'MuB', 'GW_Maechtigk_ungesaettigte_BZ.shp')

# Load Layers
print("Loading layers into QGIS...")
wells_layer = QgsVectorLayer(wells_path + "|layername=wells", "Topmost Aquifer Wells", "ogr")
bg_layer = QgsVectorLayer(shp_path, "Groundwater Distance (MuB)", "ogr")

if not wells_layer.isValid() or not bg_layer.isValid():
    print("Error: Could not load layers. Check paths.")
else:
    # Add to project
    QgsProject.instance().addMapLayer(bg_layer)
    QgsProject.instance().addMapLayer(wells_layer)

    # Style the wells by 'is_topmost'
    print("Applying categorized styling to wells...")
    categories = []
    
    # Category for True (Topmost)
    symbol_true = QgsMarkerSymbol.createSimple({'name': 'circle', 'color': 'blue', 'size': '3'})
    category_true = QgsRendererCategory('True', symbol_true, 'Topmost Aquifer')
    categories.append(category_true)
    
    # Category for False (Deep Aquifer)
    symbol_false = QgsMarkerSymbol.createSimple({'name': 'circle', 'color': 'red', 'size': '3'})
    category_false = QgsRendererCategory('False', symbol_false, 'Deep Aquifer')
    categories.append(category_false)

    renderer = QgsCategorizedSymbolRenderer('is_topmost', categories)
    wells_layer.setRenderer(renderer)
    wells_layer.triggerRepaint()

    print("QGIS setup complete.")
