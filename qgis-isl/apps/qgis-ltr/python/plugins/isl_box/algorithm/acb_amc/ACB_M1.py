# -*- coding: utf-8 -*-

"""
***************************************************************************
    ACB_M1.py
    ---------------------
    Date                 : Mai 2021
    Copyright            : (C) 2021 par ISL
    Email                : godet@isl.fr, planque@isl.fr
***************************************************************************
"""

__author__ = "Nicolas GODET, Baptiste PLANQUE"
__date__ = "Mai 2021"
__copyright__ = "(C) 2021, ISL, Nicolas GODET, Baptiste PLANQUE"

from qgis.analysis import QgsZonalStatistics
from qgis.core import (
    NULL,
    QgsFeature,
    QgsFeatureSink,
    QgsField,
    QgsFields,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingException,
    QgsProcessingParameterEnum,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterField,
    QgsProcessingParameterMultipleLayers,
    QgsProcessingParameterNumber,
    QgsProcessingParameterVectorLayer,
)
from qgis.PyQt.QtCore import QVariant

from .utils import (
    classeHEau,
    classes,
    logements_dommages_surfaciques as dommages_surfaciques,
    logements_dommages_unitaires as dommages_unitaires,
    rasterValue_from_point,
    rasterValue_from_polygon,
)

# Le cahier des charges du script :
# https://gitlab.nicodet.fr/isl/isl_box/-/issues/3


class ACB_M1(QgsProcessingAlgorithm):
    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    TYPE = "TYPE"
    RASTER = "RASTER"
    LOGEMENT = "LOGEMENT"
    ETAGE = "ETAGE"
    SURFACE = "SURFACE"
    SOUS_SOL = "SOUS_SOL"
    Z = "Z"
    SURELEVATION = "SURELEVATION"
    SUBMERSION = "SUBMERSION"

    __OPTION_SUB = ["< 48h", "> 48h"]
    __TYPE_RASTER = ["Surface libre", "Hauteur d'eau"]

    def initAlgorithm(self, config=None):  # pylint: disable=unused-argument

        # Initialisation des paramètres
        # Couche vectorielle
        self.addParameter(
            QgsProcessingParameterVectorLayer(
                self.INPUT,
                "Base de données des logements",
                types=[QgsProcessing.TypeVectorPoint, QgsProcessing.TypeVectorPolygon],
                defaultValue=None,
            )
        )
        # Couche raster
        self.addParameter(
            QgsProcessingParameterMultipleLayers(
                self.RASTER,
                "Raster(s) d'entrée",
                layerType=QgsProcessing.TypeRaster,
                defaultValue=None,
            )
        )
        self.addParameter(
            QgsProcessingParameterEnum(
                self.TYPE,
                "Type de raster(s)",
                options=self.__TYPE_RASTER,
                allowMultiple=False,
                defaultValue=[self.__TYPE_RASTER[0]],
            )
        )
        # Durée de submersion
        self.addParameter(
            QgsProcessingParameterEnum(
                self.SUBMERSION,
                "Durée de submersion",
                options=self.__OPTION_SUB,
                allowMultiple=False,
                defaultValue=[self.__OPTION_SUB[0]],
            )
        )
        # == Champs de la couche vectorielle ==
        # Type de logement
        self.addParameter(
            QgsProcessingParameterField(
                self.LOGEMENT,
                "Champ indiquant le type de logement",
                type=QgsProcessingParameterField.String,
                parentLayerParameterName=self.INPUT,
                allowMultiple=False,
                defaultValue="",
            )
        )
        # Nombre d'étages
        self.addParameter(
            QgsProcessingParameterField(
                self.ETAGE,
                "Champ indiquant le nombre d'étages du logement",
                type=QgsProcessingParameterField.Numeric,
                parentLayerParameterName=self.INPUT,
                allowMultiple=False,
                defaultValue="",
            )
        )
        # Surface du logement
        self.addParameter(
            QgsProcessingParameterField(
                self.SURFACE,
                "Champ indiquant la surface du logement",
                type=QgsProcessingParameterField.Numeric,
                parentLayerParameterName=self.INPUT,
                allowMultiple=False,
                defaultValue="",
            )
        )
        # Sous-sol
        self.addParameter(
            QgsProcessingParameterField(
                self.SOUS_SOL,
                "Champ indiquant la présence d'un sous-sol",
                type=QgsProcessingParameterField.Any,
                parentLayerParameterName=self.INPUT,
                allowMultiple=False,
                defaultValue="",
            )
        )
        # Z_plancher
        self.addParameter(
            QgsProcessingParameterField(
                self.Z,
                "Cote de plancher du logement",
                optional=True,
                type=QgsProcessingParameterField.Numeric,
                parentLayerParameterName=self.INPUT,
                allowMultiple=False,
                defaultValue="",
            )
        )
        # Surelevation du logement
        self.addParameter(
            QgsProcessingParameterNumber(
                self.SURELEVATION,
                "Critère de surélévation du plancher",
                type=QgsProcessingParameterNumber.Double,
                defaultValue=0,
                optional=True,
            )
        )
        # == Sortie ==
        # Couche de sortie
        self.addParameter(
            QgsProcessingParameterFeatureSink(
                self.OUTPUT,
                "Base de données des logements avec dommages",
                createByDefault=True,
                defaultValue=None,
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        # Import des paramètres en tant que variables
        logementLayer = self.parameterAsVectorLayer(parameters, self.INPUT, context)
        if logementLayer is None:
            raise QgsProcessingException(self.invalidSourceError(parameters, self.INPUT))

        rasters = self.parameterAsLayerList(parameters, self.RASTER, context)
        type_raster = self.__TYPE_RASTER[self.parameterAsEnum(parameters, self.TYPE, context)]
        if None in rasters:
            raise QgsProcessingException(self.invalidRasterError(parameters, self.RASTER))

        champ_type = self.parameterAsString(parameters, self.LOGEMENT, context)
        champ_etage = self.parameterAsString(parameters, self.ETAGE, context)
        champ_surface = self.parameterAsString(parameters, self.SURFACE, context)
        champ_ssols = self.parameterAsString(parameters, self.SOUS_SOL, context)
        champ_Z = self.parameterAsString(parameters, self.Z, context)
        surelev = self.parameterAsDouble(parameters, self.SURELEVATION, context)
        duree = self.__OPTION_SUB[self.parameterAsEnum(parameters, self.SUBMERSION, context)]

        if type_raster == self.__TYPE_RASTER[0] and champ_Z == "":
            raise QgsProcessingException(
                'le champ "Z" est obligatoire car un raster de surface libre est spécifié en entrée.'
            )

        champs = QgsFields()
        champs.extend(logementLayer.fields())
        for raster in rasters:
            if type_raster == self.__TYPE_RASTER[0]:
                champs.append(QgsField("SL_{}".format(raster.name()[:7]), QVariant.Double))
            champs.append(QgsField("H_{}".format(raster.name()[:7]), QVariant.Double))
            champs.append(QgsField("D_{}".format(raster.name()[:7]), QVariant.Double))

        (sink, dest_id) = self.parameterAsSink(
            parameters, self.OUTPUT, context, champs, logementLayer.wkbType(), logementLayer.sourceCrs()
        )
        if sink is None:
            raise QgsProcessingException(self.invalidSinkError(parameters, self.OUTPUT))

        total = 100.0 / logementLayer.featureCount() if logementLayer.featureCount() else 0
        logements = logementLayer.getFeatures()
        attrLogements = logementLayer.fields().names()

        for current, logement in enumerate(logements):
            # Stop l'algorithm si le boutton Annulé a été cliqué
            if feedback.isCanceled():
                break

            # Progression
            feedback.setProgress(int(current * total))

            # Initialisation de l'entité
            destFeat = QgsFeature()
            # Attribution de la liste de champs
            destFeat.setFields(champs)
            # Récupération de la géométrie de l'entité source
            logementGeom = logement.geometry()
            destFeat.setGeometry(logementGeom)

            attrDest = []
            for attr in attrLogements:
                attrDest.append(logement[attr])

            for raster in rasters:
                if logementGeom.type() == 0:  # Point
                    value = rasterValue_from_point(raster, logementGeom)
                elif logementGeom.type() == 2:  # Polygon
                    value = rasterValue_from_polygon(raster, logementGeom, QgsZonalStatistics.Median)

                if type_raster == self.__TYPE_RASTER[0]:  # Surface libre
                    attrDest.append(value)
                    h_eau = value - (logement[champ_Z] + surelev)
                elif type_raster == self.__TYPE_RASTER[1]:  # Hauteur d'eau
                    h_eau = value - surelev
                attrDest.append(h_eau)

                # Calcul des dommages
                type_habitation = self.habitation(logement, champ_type, champ_etage, champ_ssols)
                classe = classes[classeHEau(h_eau)]
                if logement[champ_surface] == NULL:
                    dommage = dommages_unitaires[duree][type_habitation][classe]
                else:
                    dommage = dommages_surfaciques[duree][type_habitation][classe] * logement[champ_surface]
                attrDest.append(dommage)
                # Fin de la boucle

            destFeat.setAttributes(attrDest)

            sink.addFeature(destFeat, QgsFeatureSink.FastInsert)

        return {
            self.OUTPUT: dest_id,
        }

    def habitation(self, feature, champ_type, champ_etage, champ_ssols):
        """
        Prend en entrée une entité et les champs utiles définis en paramètres du script
        Retourne un type unique (cf. les feuilles de calcul Excel)
        """
        if feature[champ_type].lower() in ["collectif", "lc", "appartement", "ap"]:
            string = "LC-"
        elif feature[champ_type].lower() in ["individuel", "hi", "maison", "ma"]:
            string = "HI-"
            if int(feature[champ_etage]) > 0:
                string += "AE-"
            else:
                string += "SE-"
        if str(feature[champ_ssols]).lower() in ["null", "non", "0"]:
            string += "SS"
        else:
            string += "AS"
        return string

    # Les fonctions obligatoires
    def name(self):
        return "calculacbm1"

    def displayName(self):
        return "2.1 - M1 : Calcul des dommages aux logements"

    def shortHelpString(self):
        return """
        <h2>Description de l'algorithme</h2>
        <p>L'algorithme permet de calculer les dommages aux logements dans le cadre d'une Analyse Co&ucirc;ts B&eacute;n&eacute;fices pour plusieurs sc&eacute;narios de conditions hydrauliques</p>
        <h2>Param&egrave;tres en entr&eacute;e</h2>
        <h3>Base de donn&eacute;es des logements</h3>
        <p>Couche vectorielle de la base de donn&eacute;es des logements au format points ou polygones.</p>
        <h3>Raster(s) des sc&eacute;narios d'inondation</h3>
        <p>Couche(s) raster du (ou des) sc&eacute;narios d'inondation. Ces rasters peuvent &ecirc;tre les rasters de la surface libre ou des hauteurs d'eau.</p>
        <h3>Type de raster(s)</h3>
        <p>Prermet de pr&eacute;ciser s'il s'agit des rasters de surface libre ou des hauteurs d'eau.</p>
        <h3>Dur&eacute;e de submersion</h3>
        <p>Pr&eacute;cise la dur&eacute;e de submersion pour l'application des courbes de dommage.</p>
        <h3>Champ indiquant le type de logement</h3>
        <p>Champ pr&eacute;cisant s'il s'agit d'un habitant individuel ou collectif.</p>
        <p>TODO: lister les chaines accept&eacute;es.</p>
        <h3>Champ indiquant le nombre d'&eacute;tages du logement</h3>
        <p>Champ pr&eacute;cisant le nombre d'&eacute;tage du logement.</p>
        <p>Type : Nombre</p>
        <h3>Champ indiquant la surface du logement</h3>
        <p>Champ pr&eacute;cisant la surface du logement.</p>
        <p>Type : Nombre</p>
        <h3>Champ indiquant la pr&eacute;sence d'un sous-sol</h3>
        <p>Champ pr&eacute;cisant si le logement poss&egrave;de un sous-sol ou non. L'algorithme teste sur le champ est null, indique 'non' ou 0.</p>
        <p>Type : Nombre ou chaine de caract&egrave;res</p>
        <h3>Champ indiquant la cote du plancher</h3>
        <p>Champ pr&eacute;cisant la cote altim&eacute;trique du plancher du logement. Il peut s'agir de la cote du terrain naturel ou de la cote corrig&eacute;e int&eacute;grant une &eacute;ventuelle sur&eacute;l&eacute;vation.</p>
        <p>Type : Nombre</p>
        <h3>Crit&egrave;re de sur&eacute;l&eacute;vation du plancher</h3>
        <p>Permet de pr&eacute;ciser une sur&eacute;l&eacute;vation du plancher.</p>
        <h2>Sorties</h2>
        <h3>Base de donn&eacute;es des logements avec dommages</h3>
        <p>Reprend la g&eacute;om&eacute;trie et les champs de la couche d'entr&eacute;e avec l'information sur la surface libre et/ou la hauteur d'eau dans le logement et les dommages engendr&eacute;s.</p>
        <p></p>
        <p align="right">Auteur de l'algorithme : Baptiste PLANQUE, Nicolas GODET</p>
        <p align="right">Auteur de l'aide : Nicolas GODET</p>
        """

    def group(self):
        return "ACB/AMC"

    def groupId(self):
        return "acbamc"

    def createInstance(self):
        return ACB_M1()
