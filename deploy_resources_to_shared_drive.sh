#!/bin/bash
set -e 

# auteur : Régis Haubourg 
# Licence GPLV3
# 26/05/2021


echo "** Deployes some resources to a shared drive **
"
S_DIR="/mnt/s/QGIS/custom"

# Global settings et contraintes 
echo "Copies global settings"
cp qgis-isl/apps/qgis-isl/qgis_global_settings.ini $S_DIR/QGIS/

echo "Copies qgis_constrained_settings.yml"
cp qgis-isl/apps/qgis-isl/qgis_constrained_settings.yml $S_DIR/QGIS/


# Startup project 
echo "Copies startup project"
cp qgis-isl/apps/qgis-isl/startup_project.qgs $S_DIR/


echo -e "--------"

echo -e "** End **"

echo -e "--------"




