# -*- coding: utf-8 -*-

"""
***************************************************************************
    photo2shape_plugin.py
    ---------------------
    Date                 : February 2010
    Copyright            : (C) 2010-2018 by Alexander Bruy
    Email                : alexander dot bruy at gmail dot com
***************************************************************************
*                                                                         *
*   This program is free software; you can redistribute it and/or modify  *
*   it under the terms of the GNU General Public License as published by  *
*   the Free Software Foundation; either version 2 of the License, or     *
*   (at your option) any later version.                                   *
*                                                                         *
***************************************************************************
"""

__author__ = 'Alexander Bruy'
__date__ = 'February 2010'
__copyright__ = '(C) 2010-2018, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os

from qgis.PyQt.QtCore import QCoreApplication, QTranslator
from qgis.PyQt.QtGui import QIcon
from qgis.PyQt.QtWidgets import QAction

from qgis.core import QgsApplication, QgsVectorLayer, QgsProject

from photo2shape.gui.photo2shapedialog import Photo2ShapeDialog
from photo2shape.gui.aboutdialog import AboutDialog

from photo2shape.photoimportertask import PhotoImporterTask

pluginPath = os.path.dirname(__file__)


class Photo2ShapePlugin:
    def __init__(self, iface):
        self.iface = iface

        locale = QgsApplication.locale()
        qmPath = '{}/i18n/photo2shape_{}.qm'.format(pluginPath, locale)

        if os.path.exists(qmPath):
            self.translator = QTranslator()
            self.translator.load(qmPath)
            QCoreApplication.installTranslator(self.translator)

    def initGui(self):
        self.actionRun = QAction(self.tr('Photo2Shape'), self.iface.mainWindow())
        self.actionRun.setIcon(QIcon(os.path.join(pluginPath, 'icons', 'photo2shape.svg')))
        self.actionRun.setObjectName('runPhoto2Shape')

        self.actionAbout = QAction(self.tr('About Photo2Shape…'), self.iface.mainWindow())
        self.actionAbout.setIcon(QgsApplication.getThemeIcon('/mActionHelpContents.svg'))
        self.actionRun.setObjectName('aboutPhoto2Shape')

        self.iface.addPluginToVectorMenu(self.tr('Photo2Shape'), self.actionRun)
        self.iface.addPluginToVectorMenu(self.tr('Photo2Shape'), self.actionAbout)
        self.iface.addVectorToolBarIcon(self.actionRun)

        self.actionRun.triggered.connect(self.run)
        self.actionAbout.triggered.connect(self.about)

        self.taskManager = QgsApplication.taskManager()

    def unload(self):
        self.iface.removePluginVectorMenu(self.tr('Photo2Shape'), self.actionRun)
        self.iface.removePluginVectorMenu(self.tr('Photo2Shape'), self.actionAbout)
        self.iface.removeVectorToolBarIcon(self.actionRun)

    def run(self):
        dlg = Photo2ShapeDialog()
        if dlg.exec_():
            photos = dlg.photosDirectory()
            filePath = dlg.outputFile()
            encoding = dlg.encoding()
            backend = dlg.backend()
            recurse = dlg.recurse()
            append = dlg.append()
            addToCanvas = dlg.addToCanvas()

            task = PhotoImporterTask(photos, filePath, encoding, backend, recurse, append, addToCanvas)
            task.importComplete.connect(self.importCompleted)
            task.errorOccurred.connect(self.importErrored)

            self.taskManager.addTask(task)

    def about(self):
        d = AboutDialog()
        d.exec_()

    def tr(self, text):
        return QCoreApplication.translate('Photo2Shape', text)

    def importCompleted(self, fileName, addToCanvas):
        if addToCanvas:
            layer = QgsVectorLayer(fileName, os.path.splitext(os.path.basename(fileName))[0], 'ogr')
            if layer.isValid():
                QgsProject.instance().addMapLayer(layer)

        self.iface.messageBar().pushSuccess(self.tr('Photo2Shape'), self.tr('Photos imported successfully.'))

    def importErrored(self, error):
        self.iface.messageBar().pushWarning(self.tr('Photo2Shape'), error)
