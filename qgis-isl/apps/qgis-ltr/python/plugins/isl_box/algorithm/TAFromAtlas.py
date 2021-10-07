# -*- coding: utf-8 -*-

"""
***************************************************************************
    exzeco.py
    ---------------------
    Date                 : Avril 2021
    Copyright            : (C) 2021 par ISL
    Email                : godet@isl.fr
***************************************************************************
"""

from qgis.core import (
    QgsCoordinateTransform,
    QgsCsException,
    QgsFeature,
    QgsFeatureSink,
    QgsField,
    QgsFields,
    QgsGeometry,
    QgsLayoutItemRegistry,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterCrs,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterLayout,
    QgsProcessingParameterLayoutItem,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QVariant


class TAFromAtlas(QgsProcessingAlgorithm):
    MEP = "MEP"
    CARTE = "CARTE"
    OUTPUT_SCR = "OUTPUT_SCR"
    OUTPUT = "OUTPUT"

    _FEATURES = []

    def initAlgorithm(self, config=None):  # pylint: disable=unused-argument

        self.addParameter(
            QgsProcessingParameterLayout(
                self.MEP,
                "Mise en page",
                defaultValue=None,
            )
        )
        self.addParameter(
            QgsProcessingParameterLayoutItem(
                self.CARTE,
                "Carte",
                parentLayoutParameterName=self.MEP,
                defaultValue=None,
                itemType=QgsLayoutItemRegistry.LayoutMap,
            )
        )
        self.addParameter(
            QgsProcessingParameterCrs(
                self.OUTPUT_SCR,
                "Système de coordonnées",
                defaultValue="EPSG:2154",
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                "Tableau d'assemblage",
                type=QgsProcessing.TypeVectorPolygon,
                createByDefault=True,
                defaultValue=None,
            )
        )

    def prepareAlgorithm(self, parameters, context, feedback):
        mep = self.parameterAsLayout(parameters, self.MEP, context)
        carte = self.parameterAsLayoutItem(parameters, self.CARTE, context, mep)
        outputShpScr = self.parameterAsCrs(parameters, self.OUTPUT_SCR, context)

        atlas = mep.atlas()
        atlasFeaturesCount = atlas.count()

        atlas.setEnabled(True)
        atlas.beginRender()
        atlas.first()

        champs = QgsFields()
        champs.append(QgsField("ID", QVariant.Int))
        champs.append(QgsField("Nom", QVariant.String))
        champs.append(QgsField("Largeur", QVariant.Double))
        champs.append(QgsField("Hauteur", QVariant.Double))
        champs.append(QgsField("Echelle", QVariant.Double))
        champs.append(QgsField("Rotation", QVariant.Double))

        total = 100.0 / atlasFeaturesCount

        for i in range(atlasFeaturesCount):
            if feedback.isCanceled():
                break

            feedback.setProgress(int(i * total))

            emprise = QgsGeometry.fromQPolygonF(carte.visibleExtentPolygon())
            if carte.crs() != outputShpScr:
                try:
                    emprise.transform(QgsCoordinateTransform(carte.crs(), outputShpScr, context.transformContext()))
                except QgsCsException:
                    feedback.reportError("Erreur lors de la reprojection vers le système de coordonnées de destination")
                    continue

            atlasId = atlas.currentFeatureNumber() + 1
            nom = atlas.currentFilename()
            largeur = carte.rect().width()
            hauteur = carte.rect().height()
            echelle = carte.scale()
            rotation = carte.mapRotation()

            feature = QgsFeature()
            feature.setFields(champs)
            feature.setGeometry(emprise)
            feature.setAttributes([atlasId, nom, largeur, hauteur, echelle, rotation])

            self._FEATURES.append(feature)

            atlas.next()

        atlas.endRender()

        return True

    def processAlgorithm(self, parameters, context, feedback):
        outputShpScr = self.parameterAsCrs(parameters, self.OUTPUT_SCR, context)

        champs = QgsFields()
        champs.append(QgsField("ID", QVariant.Int))
        champs.append(QgsField("Nom", QVariant.String))
        champs.append(QgsField("Largeur", QVariant.Double))
        champs.append(QgsField("Hauteur", QVariant.Double))
        champs.append(QgsField("Echelle", QVariant.Double))
        champs.append(QgsField("Rotation", QVariant.Double))

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            champs,
            QgsWkbTypes.Polygon,
            outputShpScr,
        )

        feedback.setProgressText("Finalisation de l'algorithme...")

        for f in self._FEATURES:
            sink.addFeature(f, QgsFeatureSink.FastInsert)

        feedback.setProgress(100)

        return {
            self.OUTPUT: dest_id,
        }

    def name(self):
        return "tafromatlas"

    def displayName(self):
        return "Créer le tableau d'assemblage depuis un atlas de mise en page"

    def group(self):
        return "Mise en page"

    def groupId(self):
        return "mep"

    def createInstance(self):
        return TAFromAtlas()
