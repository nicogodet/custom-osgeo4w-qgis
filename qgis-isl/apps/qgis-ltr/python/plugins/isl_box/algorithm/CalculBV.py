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

__author__ = "Nicolas GODET"
__date__ = "Avril 2021"
__copyright__ = "(C) 2021, ISL, Nicolas GODET"

from qgis.core import (
    QgsFeature,
    QgsFeatureSink,
    QgsField,
    QgsFields,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingMultiStepFeedback,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterRasterLayer,
    QgsProcessingParameterVectorLayer,
    QgsProcessingUtils,
    QgsVectorLayer,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QVariant

import processing


class CalculBV(QgsProcessingAlgorithm):
    INPUT = "INPUT"
    POINTS = "POINTS"
    OUTPUT = "OUTPUT"

    def initAlgorithm(self, config=None):  # pylint: disable=unused-argument
        self.addParameter(
            QgsProcessingParameterRasterLayer(
                self.INPUT,
                "Sens de drainage (sortie r.watershed)",
                defaultValue=None,
            )
        )
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.POINTS,
                "Exutoires (un ou plusieurs points)",
                types=[QgsProcessing.TypeVectorPoint],
                defaultValue=None,
            )
        )
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                "Bassin-versant",
                type=QgsProcessing.TypeVectorPolygon,
                createByDefault=True,
                defaultValue=None,
            )
        )

    def processAlgorithm(self, parameters, context, model_feedback):
        drainage = self.parameterAsRasterLayer(parameters, self.INPUT, context)
        pointsLayer = self.parameterAsVectorLayer(parameters, self.POINTS, context)

        champs = QgsFields()
        champs.append(QgsField("ID", QVariant.Int))
        champs.append(QgsField("Surface", QVariant.Double))

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            champs,
            QgsWkbTypes.Polygon,
            context.project().crs(),
        )

        rasterBV = QgsProcessingUtils.generateTempFilename("rasterBV.tif")

        nbPoints = pointsLayer.featureCount()

        feedback = QgsProcessingMultiStepFeedback(2 * nbPoints, model_feedback)
        outputs = {}

        for current, pointFeature in enumerate(pointsLayer.getFeatures()):
            feedback.setCurrentStep(current * nbPoints)
            if feedback.isCanceled():
                return {}

            pointGeom = pointFeature.geometry()
            if pointGeom.isMultipart():
                coord = "{x},{y}".format(x=pointGeom.asMultiPoint()[0].x(), y=pointGeom.asMultiPoint()[0].y())
            else:
                coord = "{x},{y}".format(x=pointGeom.asPoint().x(), y=pointGeom.asPoint().y())

            feedback.setProgressText(
                "Calcul du bassin versant pour l'exutoire {current} de coordonnées {coord}".format(
                    current=current + 1, coord=coord
                )
            )
            # r.water.outlet
            alg_params = {
                "GRASS_RASTER_FORMAT_META": "",
                "GRASS_RASTER_FORMAT_OPT": "",
                "GRASS_REGION_CELLSIZE_PARAMETER": 0,
                "GRASS_REGION_PARAMETER": None,
                "coordinates": coord,
                "input": drainage.source(),
                "output": rasterBV,
            }
            outputs["Rwateroutlet"] = processing.run(
                "grass7:r.water.outlet", alg_params, context=context, feedback=feedback, is_child_algorithm=True
            )

            feedback.setCurrentStep(current * nbPoints + 1)
            if feedback.isCanceled():
                return {}

            # Polygoniser (raster vers vecteur)
            alg_params = {
                "BAND": 1,
                "EIGHT_CONNECTEDNESS": False,
                "EXTRA": "",
                "FIELD": "DN",
                "INPUT": rasterBV,
                "OUTPUT": QgsProcessing.TEMPORARY_OUTPUT,
            }
            outputs["Polygoniser"] = processing.run(
                "gdal:polygonize", alg_params, context=context, feedback=feedback, is_child_algorithm=True
            )

            bvLayer = QgsVectorLayer(outputs["Polygoniser"]["OUTPUT"], "BV", "ogr")
            for bv in bvLayer.getFeatures():
                feature = QgsFeature()
                feature.setGeometry(bv.geometry())
                feature.setFields(champs)
                feature.setAttributes([current, bv.geometry().area()])

                sink.addFeature(feature, QgsFeatureSink.FastInsert)

        feedback.setProgress(100)

        return {
            self.OUTPUT: dest_id,
        }

    def name(self):
        return "calculbv"

    def displayName(self):
        return "Calcul du bassin versant à partir d'une couche de points"

    def group(self):
        return "Analyse topographique"

    def groupId(self):
        return "analysetopo"

    def createInstance(self):
        return CalculBV()
