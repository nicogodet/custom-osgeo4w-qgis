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
    QgsCoordinateTransform,
    QgsFeature,
    QgsFeatureSink,
    QgsField,
    QgsFields,
    QgsProcessing,
    QgsProcessingAlgorithm,
    QgsProcessingParameterCrs,
    QgsProcessingParameterFeatureSink,
    QgsProcessingParameterFile,
    QgsVectorLayer,
    QgsWkbTypes,
)
from qgis.PyQt.QtCore import QVariant


class PretraitementSirene(QgsProcessingAlgorithm):

    INPUT = "INPUT"
    OUTPUT = "OUTPUT"
    OUTPUT_SCR = "OUTPUT_SCR"

    def name(self):
        return "pretraitementsirene"

    def displayName(self):
        return "1.1 - Prétraitement de la base SIRENE extraite d'OpenDataSoft au format .kml"

    def group(self):
        return "ACB/AMC"

    def groupId(self):
        return "acbamc"

    def createInstance(self):
        return PretraitementSirene()

    def initAlgorithm(self, config=None):  # pylint: disable=unused-argument
        self.addParameter(
            QgsProcessingParameterFile(
                self.INPUT,
                "Export SIRENEv3 OpenDataSoft",
                behavior=QgsProcessingParameterFile.File,
                fileFilter="Fichiers KML (*.kml)",
                defaultValue=None,
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
                "Base SIRENE pré-traîtée",
                type=QgsProcessing.TypeVectorPoint,
                createByDefault=True,
                defaultValue=None,
            )
        )

    def processAlgorithm(self, parameters, context, feedback):
        kmlPath = self.parameterAsString(parameters, self.INPUT, context)
        outputShpScr = self.parameterAsCrs(parameters, self.OUTPUT_SCR, context)
        kml = QgsVectorLayer(kmlPath, "kml")
        kml.setProviderEncoding("UTF-8")

        kmlFeatCount = kml.featureCount()
        total = 100.0 / kmlFeatCount

        mapFieldDest = {}
        for k, v in mapFieldSource.items():
            if v["dest"] != "":
                mapFieldDest[v["dest"]] = {"source": k, "type": v["type"]}

        mapFieldDest = self.reorder_items(mapFieldDest, orderDest)

        champs = QgsFields()
        for k, v in mapFieldDest.items():
            champs.append(QgsField(k, v["type"]))
        champs.append(QgsField("cateff", QVariant.String))
        champs.append(QgsField("mineff", QVariant.Int))
        champs.append(QgsField("maxeff", QVariant.Int))
        champs.append(QgsField("valeff", QVariant.Double))

        (sink, dest_id) = self.parameterAsSink(
            parameters,
            self.OUTPUT,
            context,
            champs,
            QgsWkbTypes.Point,
            outputShpScr,
        )

        transform = False
        if kml.crs() != outputShpScr:
            transform = True

        for i, kmlFeat in enumerate(kml.getFeatures()):
            if feedback.isCanceled():
                break

            feedback.setProgress(int(i * total))

            destFeat = QgsFeature()
            destFeat.setFields(champs)

            kmlFeatGeom = kmlFeat.geometry()

            if transform:
                kmlFeatGeom.transform(QgsCoordinateTransform(kml.crs(), outputShpScr, context.transformContext()))

            destFeat.setGeometry(kmlFeatGeom)

            attrDest = []
            for v in mapFieldDest.values():
                attrDest.append(kmlFeat[v["source"]])

            trancheEff = kmlFeat["trancheeffectifsetablissement"]
            if str(trancheEff) != "NULL":
                attrDest.append(conversionValEmploye[trancheEff]["categorie"])
                attrDest.append(conversionValEmploye[trancheEff]["min"])
                attrDest.append(conversionValEmploye[trancheEff]["max"])
                attrDest.append(conversionValEmploye[trancheEff]["valeur"])
            else:
                attrDest.append(conversionValEmploye["0 salarié"]["categorie"])
                attrDest.append(conversionValEmploye["0 salarié"]["min"])
                attrDest.append(conversionValEmploye["0 salarié"]["max"])
                attrDest.append(conversionValEmploye["0 salarié"]["valeur"])

            destFeat.setAttributes(attrDest)

            sink.addFeature(destFeat, QgsFeatureSink.FastInsert)

        return {
            self.OUTPUT: dest_id,
        }

    # https://stackoverflow.com/a/53068406
    def reorder_items(self, d, keys):
        d = d.copy()  # we're going to destructively modify d, so make a copy first
        result = {}
        for key in keys:
            if key in d:
                result[key] = d.pop(key)
        # the user might not have supplied all the keys belonging to d,
        # so insert anything we haven't touched yet
        result.update(d)
        return result


mapFieldSource = {
    "Name": {"dest": "", "type": QVariant.String},
    "activiteprincipaleetablissement": {"dest": "CodeNAF", "type": QVariant.String},
    "activiteprincipaleregistremetiersetablissement": {"dest": "", "type": QVariant.String},
    "activiteprincipaleunitelegale": {"dest": "", "type": QVariant.String},
    "adresseetablissement": {"dest": "adresse", "type": QVariant.String},
    "altitudeMode": {"dest": "", "type": QVariant.String},
    "altitudemoyennecommuneetablissement": {"dest": "", "type": QVariant.String},
    "anneecategorieentreprise": {"dest": "", "type": QVariant.String},
    "anneeeffectifsetablissement": {"dest": "", "type": QVariant.String},
    "anneeeffectifsunitelegale": {"dest": "", "type": QVariant.String},
    "begin": {"dest": "", "type": QVariant.String},
    "caractereemployeuretablissement": {"dest": "", "type": QVariant.String},
    "caractereemployeurunitelegale": {"dest": "", "type": QVariant.String},
    "categorieentreprise": {"dest": "", "type": QVariant.String},
    "categoriejuridiqueunitelegale": {"dest": "", "type": QVariant.String},
    "classeetablissement": {"dest": "", "type": QVariant.String},
    "classeunitelegale": {"dest": "", "type": QVariant.String},
    "codearrondissementetablissement": {"dest": "", "type": QVariant.String},
    "codecedex2etablissement": {"dest": "", "type": QVariant.String},
    "codecedexetablissement": {"dest": "", "type": QVariant.String},
    "codecommune2etablissement": {"dest": "", "type": QVariant.String},
    "codecommuneetablissement": {"dest": "codecom", "type": QVariant.String},
    "codedepartementetablissement": {"dest": "", "type": QVariant.String},
    "codeepcietablissement": {"dest": "", "type": QVariant.String},
    "codepaysetranger2etablissement": {"dest": "", "type": QVariant.String},
    "codepaysetrangeretablissement": {"dest": "", "type": QVariant.String},
    "codepostal2etablissement": {"dest": "", "type": QVariant.String},
    "codepostaletablissement": {"dest": "cpet", "type": QVariant.String},
    "coderegionetablissement": {"dest": "", "type": QVariant.String},
    "complementadresse2etablissement": {"dest": "", "type": QVariant.String},
    "complementadresseetablissement": {"dest": "", "type": QVariant.String},
    "datecreationetablissement": {"dest": "dcret", "type": QVariant.String},
    "datecreationunitelegale": {"dest": "", "type": QVariant.String},
    "datedebutetablissement": {"dest": "", "type": QVariant.String},
    "datedebutunitelegale": {"dest": "", "type": QVariant.String},
    "datederniertraitementetablissement": {"dest": "", "type": QVariant.String},
    "datederniertraitementunitelegale": {"dest": "", "type": QVariant.String},
    "datefermetureetablissement": {"dest": "", "type": QVariant.String},
    "datefermetureunitelegale": {"dest": "", "type": QVariant.String},
    "denominationunitelegale": {"dest": "denomut", "type": QVariant.String},
    "denominationusuelle1unitelegale": {"dest": "", "type": QVariant.String},
    "denominationusuelle2unitelegale": {"dest": "", "type": QVariant.String},
    "denominationusuelle3unitelegale": {"dest": "", "type": QVariant.String},
    "denominationusuelleetablissement": {"dest": "", "type": QVariant.String},
    "departementetablissement": {"dest": "", "type": QVariant.String},
    "description": {"dest": "", "type": QVariant.String},
    "distributionspeciale2etablissement": {"dest": "", "type": QVariant.String},
    "distributionspecialeetablissement": {"dest": "", "type": QVariant.String},
    "divisionetablissement": {"dest": "divisionet", "type": QVariant.String},
    "divisionunitelegale": {"dest": "", "type": QVariant.String},
    "drawOrder": {"dest": "", "type": QVariant.String},
    "economiesocialesolidaireunitelegale": {"dest": "", "type": QVariant.String},
    "end": {"dest": "", "type": QVariant.String},
    "enseigne1etablissement": {"dest": "", "type": QVariant.String},
    "enseigne2etablissement": {"dest": "", "type": QVariant.String},
    "enseigne3etablissement": {"dest": "", "type": QVariant.String},
    "epcietablissement": {"dest": "", "type": QVariant.String},
    "etablissementsiege": {"dest": "", "type": QVariant.String},
    "etatadministratifetablissement": {"dest": "etatadmi", "type": QVariant.String},
    "etatadministratifunitelegale": {"dest": "", "type": QVariant.String},
    "extrude": {"dest": "", "type": QVariant.String},
    "filename": {"dest": "", "type": QVariant.String},
    "groupeetablissement": {"dest": "groupeet", "type": QVariant.String},
    "groupeunitelegale": {"dest": "", "type": QVariant.String},
    "icon": {"dest": "", "type": QVariant.String},
    "identifiantassociationunitelegale": {"dest": "", "type": QVariant.String},
    "indicerepetition2etablissement": {"dest": "", "type": QVariant.String},
    "indicerepetitionetablissement": {"dest": "indrepet", "type": QVariant.String},
    "l1_adressage_unitelegale": {"dest": "nomut", "type": QVariant.String},
    "libellecedex2etablissement": {"dest": "", "type": QVariant.String},
    "libellecedexetablissement": {"dest": "", "type": QVariant.String},
    "libellecommune2etablissement": {"dest": "", "type": QVariant.String},
    "libellecommuneetablissement": {"dest": "comet", "type": QVariant.String},
    "libellecommuneetranger2etablissement": {"dest": "", "type": QVariant.String},
    "libellecommuneetrangeretablissement": {"dest": "", "type": QVariant.String},
    "libellepaysetranger2etablissement": {"dest": "", "type": QVariant.String},
    "libellepaysetrangeretablissement": {"dest": "", "type": QVariant.String},
    "libellevoie2etablissement": {"dest": "", "type": QVariant.String},
    "libellevoieetablissement": {"dest": "libvoieet", "type": QVariant.String},
    "naturejuridiqueunitelegale": {"dest": "", "type": QVariant.String},
    "nic": {"dest": "nic", "type": QVariant.Int},
    "nicsiegeunitelegale": {"dest": "", "type": QVariant.String},
    "nombreperiodesetablissement": {"dest": "", "type": QVariant.String},
    "nombreperiodesunitelegale": {"dest": "", "type": QVariant.String},
    "nomenclatureactiviteprincipaleetablissement": {"dest": "", "type": QVariant.String},
    "nomenclatureactiviteprincipaleunitelegale": {"dest": "", "type": QVariant.String},
    "nomunitelegale": {"dest": "", "type": QVariant.String},
    "nomusageunitelegale": {"dest": "", "type": QVariant.String},
    "numerovoie2etablissement": {"dest": "", "type": QVariant.String},
    "numerovoieetablissement": {"dest": "numvoieet", "type": QVariant.Int},
    "populationcommuneetablissement": {"dest": "", "type": QVariant.String},
    "prenom1unitelegale": {"dest": "", "type": QVariant.String},
    "prenom2unitelegale": {"dest": "", "type": QVariant.String},
    "prenom3unitelegale": {"dest": "", "type": QVariant.String},
    "prenom4unitelegale": {"dest": "", "type": QVariant.String},
    "prenomusuelunitelegale": {"dest": "", "type": QVariant.String},
    "pseudonymeunitelegale": {"dest": "", "type": QVariant.String},
    "regionetablissement": {"dest": "", "type": QVariant.String},
    "sectionetablissement": {"dest": "sectionet", "type": QVariant.String},
    "sectionunitelegale": {"dest": "", "type": QVariant.String},
    "sexeunitelegale": {"dest": "", "type": QVariant.String},
    "sigleunitelegale": {"dest": "", "type": QVariant.String},
    "siren": {"dest": "siren", "type": QVariant.String},
    "siret": {"dest": "siret", "type": QVariant.String},
    "siretsiegeunitelegale": {"dest": "", "type": QVariant.String},
    "soussectionetablissement": {"dest": "ssectionet", "type": QVariant.String},
    "soussectionunitelegale": {"dest": "", "type": QVariant.String},
    "statutdiffusionetablissement": {"dest": "", "type": QVariant.String},
    "statutdiffusionunitelegale": {"dest": "", "type": QVariant.String},
    "superficiecommuneetablissement": {"dest": "", "type": QVariant.String},
    "tessellate": {"dest": "", "type": QVariant.String},
    "timestamp": {"dest": "", "type": QVariant.String},
    "trancheeffectifsetablissement": {"dest": "tefet", "type": QVariant.String},
    "trancheeffectifsunitelegale": {"dest": "tefut", "type": QVariant.String},
    "typevoie2etablissement": {"dest": "", "type": QVariant.String},
    "typevoieetablissement": {"dest": "typevoieet", "type": QVariant.String},
    "unitepurgeeunitelegale": {"dest": "", "type": QVariant.String},
    "visibility": {"dest": "", "type": QVariant.String},
}

orderDest = (
    "siren",
    "nic",
    "siret",
)


conversionValEmploye = {
    "Etablissement non employeur": {"categorie": "NN", "min": 0, "max": 0, "valeur": 0},
    "0 salarié": {"categorie": "00", "min": 0, "max": 0, "valeur": 0},
    "1 ou 2 salariés": {"categorie": "01", "min": 1, "max": 2, "valeur": 2.3},
    "3 à 5 salariés": {"categorie": "02", "min": 3, "max": 5, "valeur": 4.71},
    "6 à 9 salariés": {"categorie": "03", "min": 6, "max": 9, "valeur": 8.17},
    "10 à 19 salariés": {"categorie": "11", "min": 10, "max": 19, "valeur": 14.3},
    "20 à 49 salariés": {"categorie": "12", "min": 20, "max": 49, "valeur": 30.4},
    "50 à 99 salariés": {"categorie": "21", "min": 50, "max": 99, "valeur": 68.8},
    "100 à 199 salariés": {"categorie": "22", "min": 100, "max": 199, "valeur": 137},
    "200 à 249 salariés": {"categorie": "31", "min": 200, "max": 249, "valeur": 223},
    "250 à 499 salariés": {"categorie": "32", "min": 250, "max": 499, "valeur": 342},
    "500 à 999 salariés": {"categorie": "41", "min": 500, "max": 999, "valeur": 683},
    "1000 à 1999 salariés": {"categorie": "42", "min": 1000, "max": 1999, "valeur": 1360},
    "2000 à 4999 salariés": {"categorie": "51", "min": 2000, "max": 4999, "valeur": 2990},
    "5000 à 9999 salariés": {"categorie": "52", "min": 5000, "max": 9999, "valeur": 6960},
    "10000 salariés et plus": {"categorie": "53", "min": 10000, "max": 99999, "valeur": 15000},
}
