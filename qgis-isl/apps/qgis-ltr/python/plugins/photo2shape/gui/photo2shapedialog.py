# -*- coding: utf-8 -*-

"""
***************************************************************************
    photo2shapedialog.py
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

from qgis.PyQt import uic
from qgis.PyQt.QtWidgets import QDialog, QDialogButtonBox, QMessageBox

from qgis.core import QgsSettings, QgsProject, QgsVectorDataProvider
from qgis.gui import QgsGui, QgsFileWidget

from photo2shape.backends import backendsRegistry

pluginPath = os.path.split(os.path.dirname(__file__))[0]
WIDGET, BASE = uic.loadUiType(os.path.join(pluginPath, 'ui', 'photo2shapedialogbase.ui'))


class Photo2ShapeDialog(BASE, WIDGET):
    def __init__(self, parent=None):
        super(Photo2ShapeDialog, self).__init__(parent)
        self.setupUi(self)

        QgsGui.instance().enableAutoGeometryRestore(self)

        settings = QgsSettings()

        self.fwPhotosDirectory.setStorageMode(QgsFileWidget.GetDirectory)
        self.fwPhotosDirectory.setDialogTitle(self.tr('Select directory'))
        self.fwPhotosDirectory.setDefaultRoot(settings.value('photo2shape/lastPhotosDirectory', os.path.expanduser('~'), str))
        self.fwPhotosDirectory.fileChanged.connect(self.updateLastPhotosPath)

        self.fwOutputFile.setStorageMode(QgsFileWidget.SaveFile)
        self.fwOutputFile.setConfirmOverwrite(True)
        self.fwOutputFile.setDialogTitle(self.tr('Select file'))
        self.fwOutputFile.setDefaultRoot(settings.value('photo2shape/lastOutputDirectory', QgsProject.instance().homePath(), str))
        self.fwOutputFile.setFilter(self.tr('ESRI Shapefile (*.shp *.SHP)'))
        self.fwOutputFile.fileChanged.connect(self.updateLastOutputPath)

        self.cmbEncoding.addItems(QgsVectorDataProvider.availableEncodings())
        encoding = settings.value('photo2shape/encoding', 'UTF-8', str)
        self.cmbEncoding.setCurrentIndex(self.cmbEncoding.findText(encoding))

        for backend in sorted(backendsRegistry.keys()):
            self.cmbBackend.addItem(backendsRegistry[backend].displayName(), backend)

        backend = settings.value('photo2shape/backend', 'exifread', str)
        self.cmbBackend.setCurrentIndex(self.cmbBackend.findData(backend))

        self.chkRecurse.setChecked(settings.value('photo2shape/recurse', True, bool))
        self.chkAppend.setChecked(settings.value('photo2shape/append', False, bool))
        self.chkAddToCanvas.setChecked(settings.value('photo2shape/addToCanvas', True, bool))

        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(False)

    def updateLastPhotosPath(self, filePath):
        self.fwPhotosDirectory.setDefaultRoot(filePath)
        QgsSettings().setValue('photo2shape/lastPhotosDirectory', os.path.dirname(filePath))
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(filePath != "" and self.fwOutputFile.filePath() != "")

    def updateLastOutputPath(self, filePath):
        self.fwOutputFile.setDefaultRoot(filePath)
        QgsSettings().setValue('photo2shape/lastOutputDirectory', os.path.dirname(filePath))
        self.buttonBox.button(QDialogButtonBox.Ok).setEnabled(filePath != "" and self.fwPhotosDirectory.filePath() != "")

    def reject(self):
        QDialog.reject(self)

    def accept(self):
        if self.chkAppend.isChecked() and not os.path.isfile(self.fwOutputFile.filePath()):
            QMessageBox.warning(self,
                                self.tr('Appending is not possible'),
                                self.tr('Output file is a new file and can not be used in the "append" mode. '
                                        'Either specify existing file or uncheck corresponding checkbox.'))
            return

        self._saveSettings()

        QDialog.accept(self)

    def _saveSettings(self):
        settings = QgsSettings()
        settings.setValue('photo2shape/encoding', self.cmbEncoding.currentText())
        settings.setValue('photo2shape/backend', self.cmbBackend.currentData())
        settings.setValue('photo2shape/recurse', self.chkRecurse.isChecked())
        settings.setValue('photo2shape/append', self.chkAppend.isChecked())
        settings.setValue('photo2shape/addToCanvas', self.chkAddToCanvas.isChecked())

    def photosDirectory(self):
        return self.fwPhotosDirectory.filePath()

    def outputFile(self):
        return self.fwOutputFile.filePath()

    def encoding(self):
        return self.cmbEncoding.currentText()

    def backend(self):
        return self.cmbBackend.currentData()

    def recurse(self):
        return self.chkRecurse.isChecked()

    def append(self):
        return self.chkAppend.isChecked()

    def addToCanvas(self):
        return self.chkAddToCanvas.isChecked()
