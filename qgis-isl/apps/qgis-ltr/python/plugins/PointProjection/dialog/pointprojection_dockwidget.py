# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PointProjectionDockWidget
                                 A QGIS plugin
 test
                             -------------------
        begin                : 2016-03-16
        git sha              : $Format:%H$
        copyright            : (C) 2016 by toto
        email                : toto@toto
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

import os

# PyQT libs
from qgis.PyQt import uic
from qgis.PyQt.QtCore import Qt, QVariant, pyqtSignal
from qgis.PyQt.QtGui import QColor
from qgis.PyQt.QtWidgets import QDockWidget, QVBoxLayout, QMessageBox

# Qgis libs
from qgis.core import (
    Qgis,
    QgsWkbTypes,
    QgsVectorLayer,
    QgsField,
    QgsDefaultValue,
    QgsFeature,
    QgsProject,
    QgsMessageLog,
    QgsExpression,
    QgsExpressionContext,
    QgsExpressionContextUtils,
)
from qgis.gui import QgsRubberBand
from qgis.utils import iface

# Matplotlib libs
from matplotlib import *
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar

# plugin libs
from ..libs.pointprojector import *

FORM_CLASS, _ = uic.loadUiType(os.path.join(os.path.dirname(__file__), "pointprojection_dockwidget_base.ui"))


class PointProjectionDockWidget(QDockWidget, FORM_CLASS):

    closingPlugin = pyqtSignal()

    def __init__(self, parent=None):
        """Constructor."""
        super(PointProjectionDockWidget, self).__init__(parent)
        # Set up the user interface from Designer.
        # After setupUI you can access any designer object by doing
        # self.<objectname>, and you can use autoconnect slots - see
        # http://qt-project.org/doc/qt-4.8/designer-using-a-ui-file.html
        # #widgets-and-dialogs-with-auto-connect
        self.setupUi(self)
        self.pointprojector = None  # the class that process projection
        self.options = {"buffer": 0, "delDupPoints": True, "spatialstep": 0}
        self.iface = iface
        self.activelayer = None  # the active layer (line vector layer)
        self.mapcanvas = self.iface.mapCanvas()
        self.rubberband = QgsRubberBand(self.mapcanvas, QgsWkbTypes.LineGeometry)  # the rubberband
        self.rubberband.setWidth(2)
        self.rubberband.setColor(QColor(Qt.red))
        # Initiate layer in combobox
        self.updateLayers()
        # Connectors
        self.pushButton_testline.clicked.connect(self.testLine)
        self.pushButton_extract.clicked.connect(self.extractPoints)
        self.checkBox_interpfield.stateChanged.connect(self.activePointFields)
        self.refresh.clicked.connect(self.updateLayers)
        self.comboBox_typeExtraction.currentIndexChanged.connect(self.switchMethod)
        QgsProject.instance().legendLayersAdded.connect(self.updateLayers)
        QgsProject.instance().layersRemoved.connect(self.updateLayers)
        QgsProject.instance().layerTreeRoot().visibilityChanged.connect(self.updateLayers)
        # figure matplotlib
        self.figure1 = plt.figure(0)
        font = {"family": "arial", "weight": "normal", "size": 12}
        rc("font", **font)
        self.canvas1 = FigureCanvas(self.figure1)
        self.ax = self.figure1.add_subplot(111)
        layout = QVBoxLayout()
        try:
            self.toolbar = NavigationToolbar(self.canvas1, self.frame_mpl, True)
            layout.addWidget(self.toolbar)
        except Exception as e:
            pass
        layout.addWidget(self.canvas1)
        self.canvas1.draw()
        self.frame_mpl.setLayout(layout)

    def testLine(self):
        """
        Action when Test button is clicked
        """
        # reinit things
        try:
            self.activelayer.selectionChanged.disconnect(self.activeLayerSelectionChanged)
        except Exception as e:
            pass
        self.activelayer = iface.activeLayer()
        self.activelayer.selectionChanged.connect(self.activeLayerSelectionChanged)
        # create pointprojector class
        layer = self.getLayerByName(self.comboBox.currentText())
        self.pointprojector = pointProjector(
            layer,
            self.comboBox_field.currentIndex() if self.comboBox_field.isEnabled() else -1,
            self.activelayer.crs(),
            self.rubberband,
        )
        # process part
        if self.activeLayerIsLine():
            fets = iface.activeLayer().selectedFeatures()
            if len(fets) > 0:  # case when a feature is selected
                fet = fets[0]
                self.options["buffer"] = self.spinBox_buffer.value()
                self.options["spatialstep"] = 0
                buffer, projectedpoints = self.pointprojector.computeProjectedPoints(fet, self.options)
                if type(projectedpoints) is type(None):
                    iface.messageBar().pushInfo("Info", "Aucun point présent dans le buffer défini.")
                else:
                    self.pointprojector.visualResultTestLine()
                    self.pointprojector.createMatPlotLibGraph(self.canvas1, self.ax)
            else:  # case when no feature is selected : reset
                self.pointprojector.resetRubberband()
                layer.removeSelection()

    def extractPoints(self):
        """
        Action when extract button is clicked
        Create temp layer with projected and interpolated points
        """
        # create pointprojector class
        layer = self.getLayerByName(self.comboBox.currentText())
        self.pointprojector = pointProjector(
            layer,
            self.comboBox_field.currentIndex() if self.comboBox_field.isEnabled() else -1,
            self.activelayer.crs(),
        )
        projectedpointstotal = []
        # process part
        if self.activeLayerIsLine():
            fets = iface.activeLayer().selectedFeatures()

            self.options["buffer"] = self.spinBox_buffer.value()
            self.options["delDupPoints"] = self.removeDuplicates.isChecked()
            self.options["spatialstep"] = (
                self.spinBox_spatialstep.value() if self.spinBox_spatialstep.isEnabled() else 0
            )
            projectCrs = iface.mapCanvas().mapSettings().destinationCrs()
            xform = QgsCoordinateTransform(
                layer.crs(),
                projectCrs,
                QgsProject.instance(),
            )

            if len(fets) == 0:  # process all line in layer
                count = iface.activeLayer().featureCount()
                for fet in iface.activeLayer().getFeatures():
                    percent = fet.id() / float(count) * 100
                    iface.statusBarIface().showMessage("Progression {} %".format(int(percent)))
                    buffer, projectedpoints = self.pointprojector.computeProjectedPoints(
                        fet,
                        self.options,
                    )
                    if type(projectedpoints) is not type(None):
                        projectedpointstotal.append([fet.id(), projectedpoints])
            else:  # process selected line in layer
                fet = fets[0]
                buffer, projectedpoints = self.pointprojector.computeProjectedPoints(
                    fet,
                    self.options,
                )
                if type(projectedpoints) is type(None):
                    iface.messageBar().pushInfo("Info", "Aucun point présent dans le buffer défini.")
                else:
                    projectedpointstotal.append([fet.id(), projectedpoints])

            # Vector layer creation
            vectorType = "Point?crs=" + str(projectCrs.authid())
            name = "Interp_" + str(layer.name())
            vl = QgsVectorLayer(vectorType, name, "memory")
            pr = vl.dataProvider()
            vl.startEditing()
            # add fields
            pr.addAttributes([QgsField("PointID", QVariant.Int)])
            pr.addAttributes(layer.fields())
            pr.addAttributes(
                [
                    QgsField("LineID", QVariant.Int),
                    QgsField("PK", QVariant.Double),
                    QgsField("Interp", QVariant.Double),
                    QgsField("Type", QVariant.String),
                ]
            )
            vl.updateFields()
            # Add features to layer
            for projectedpointstemp in projectedpointstotal:
                featid = projectedpointstemp[0]
                projectedpoints = projectedpointstemp[1]
                for projectedpoint in projectedpoints:
                    fet = QgsFeature(layer.fields())
                    # set geometry
                    fet.setGeometry(
                        QgsGeometry.fromPointXY(xform.transform(QgsPointXY(projectedpoint[1], projectedpoint[2])))
                    )
                    # set attributes
                    if projectedpoint[8] != None:
                        attribtemp = [projectedpoint[8].id()]
                        attribtemp += projectedpoint[8].attributes()
                    else:
                        attribtemp = [None] * (len(layer.fields()) + 1)
                    attribtemp.append(int(featid))
                    attribtemp.append(projectedpoint[0])
                    attribtemp.append(projectedpoint[5])
                    if projectedpoint[3] == -1:
                        attribtemp.append("interpolated")
                    else:
                        attribtemp.append("projected")
                    fet.setAttributes(attribtemp)
                    pr.addFeatures([fet])
            vl.commitChanges()
            # show layer
            QgsProject.instance().addMapLayer(vl)
            # reinit progess bar
            iface.messageBar().clearWidgets()
            iface.statusBarIface().clearMessage()

    def assignAutoField(self):
        if self.activeLayerIsLine():
            pointLayer = self.getLayerByName(self.comboBox.currentText())
            lineLayer = iface.activeLayer()

            context = QgsExpressionContext()
            context.appendScopes(QgsExpressionContextUtils.globalProjectLayerScopes(pointLayer))

            pointLayer.startEditing()
            if "PK" in list(pointLayer.attributeAliases()):
                attrIndex = list(pointLayer.attributeAliases()).index("PK")
                res = QMessageBox.question(
                    self,
                    "Champ PK existant",
                    'La couche {} possède déjà un champ "PK".' "Voulez-vous l'écraser ?".format(pointLayer.name()),
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No,
                )
                if res != QMessageBox.Yes:
                    return

                pointLayer.deleteAttribute(attrIndex)
                pointLayer.commitChanges()

            attrIndex = len(list(pointLayer.attributeAliases()))
            pointLayer.addAttribute(QgsField("PK", QVariant.Double))
            pointLayer.updateFields()

            expressionString = "line_locate_point(overlay_nearest('{}', $geometry)[0], $geometry)".format(
                lineLayer.id()
            )
            expression = QgsExpression(expressionString)
            for f in pointLayer.getFeatures():
                context.setFeature(f)
                f["PK"] = expression.evaluate(context)
                pointLayer.updateFeature(f)

            pointLayer.setDefaultValueDefinition(
                attrIndex,
                QgsDefaultValue(expressionString, applyOnUpdate=True),
            )
            pointLayer.commitChanges()

    # ********************** Tools *******************************************

    def getLayerByName(self, name1):  # layer = QgsProject.instance().mapLayersByName("layer name you like")[0]
        for layer in QgsProject.instance().mapLayers().values():
            if name1 == layer.name():
                return layer
                break
        return None

    def activeLayerSelectionChanged(self, selected, deselected, clearAndSelect):
        if self.pointprojector != None:
            self.pointprojector.resetRubberband()

    def activeLayerIsLine(self):
        layer = iface.activeLayer()
        if layer.type() == 0 and layer.geometryType() == 1:
            return True
        else:
            iface.messageBar().pushCritical("Error", "Choisir une couche vecteur de type ligne")
            return False

    def updateLayers(self):
        currentLayer = self.comboBox.currentText()

        self.comboBox.currentIndexChanged.connect(self.updateFields)

        self.comboBox.blockSignals(True)
        self.comboBox.clear()
        project = QgsProject.instance()
        for layer_id, layer in project.mapLayers().items():
            if project.layerTreeRoot().findLayer(layer_id) is not None:
                if (
                    layer.type() == 0
                    and layer.geometryType() == 0
                    and project.layerTreeRoot().findLayer(layer_id).isVisible()
                ):
                    self.comboBox.addItems([str(layer.name())])

        if currentLayer != "" and self.comboBox.findText(currentLayer, Qt.MatchFixedString) > -1:
            self.comboBox.setCurrentIndex(self.comboBox.findText(currentLayer))
        self.comboBox.blockSignals(False)

        self.updateFields()

    def updateFields(self):
        currentField = self.comboBox_field.currentText()
        self.comboBox_field.clear()
        if self.comboBox.currentText() != "":
            layer = self.getLayerByName(self.comboBox.currentText())
            for field in layer.fields():
                self.comboBox_field.addItems([str(field.name())])

        if currentField != "" and self.comboBox_field.findText(currentField, Qt.MatchFixedString) > -1:
            self.comboBox_field.setCurrentIndex(self.comboBox_field.findText(currentField, Qt.MatchFixedString))
        elif self.comboBox_field.findText("z", Qt.MatchFixedString) > -1:
            self.comboBox_field.setCurrentIndex(self.comboBox_field.findText("z", Qt.MatchFixedString))
        elif self.comboBox_field.findText("alti", Qt.MatchFixedString) > -1:
            self.comboBox_field.setCurrentIndex(self.comboBox_field.findText("alti", Qt.MatchFixedString))

    def activePointFields(self, int1):
        if int1 == 0:
            self.comboBox_field.setEnabled(False)
        else:
            self.comboBox_field.setEnabled(True)

    def switchMethod(self, int1):
        if int1 <= 1:
            self.pushButton_extract.clicked.disconnect()
            self.pushButton_extract.clicked.connect(self.extractPoints)
            self.pushButton_extract.setText("Extraction")
            self.spinBox_spatialstep.setEnabled(int1)
            self.removeDuplicates.setEnabled(True)
        elif int1 == 2:
            self.pushButton_extract.clicked.disconnect()
            self.pushButton_extract.clicked.connect(self.assignAutoField)
            self.pushButton_extract.setText('Créer un champ automatique "PK"')
            self.spinBox_spatialstep.setEnabled(False)
            self.removeDuplicates.setEnabled(False)

    def closeEvent(self, event):
        """
        Actions when closing plugin dock
        """
        try:
            self.pushButton_testline.clicked.disconnect(self.testLine)
            self.pushButton_extract.clicked.disconnect()
            self.checkBox_interpfield.stateChanged.disconnect(self.activePointFields)
            self.refresh.clicked.disconnect(self.updateLayers)
            self.comboBox_typeExtraction.currentIndexChanged.disconnect(self.switchMethod)
        except Exception as e:
            pass
        try:
            self.activelayer.selectionChanged.disconnect(self.activeLayerSelectionChanged)
        except Exception as e:
            pass
        try:
            QgsProject.instance().legendLayersAdded.disconnect(self.updateLayers)
            QgsProject.instance().layersRemoved.disconnect(self.updateLayers)
            QgsProject.instance().layerTreeRoot().visibilityChanged.disconnect(self.updateLayers)
            self.comboBox.currentIndexChanged.disconnect(self.updateFields)
        except Exception as e:
            pass
        self.rubberband.reset(QgsWkbTypes.LineGeometry)
        self.closingPlugin.emit()
        event.accept()
