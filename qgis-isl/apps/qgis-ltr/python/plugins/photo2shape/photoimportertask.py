# -*- coding: utf-8 -*-

"""
***************************************************************************
    photoimportertask.py
    ---------------------
    Date                 : November 2014
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
__date__ = 'November 2014'
__copyright__ = '(C) 2010-2018, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import os
import shutil

from qgis.PyQt.QtCore import pyqtSignal, QVariant, QCoreApplication

from qgis.core import (QgsTask,
                       Qgis,
                       QgsMessageLog,
                       QgsField,
                       QgsFields,
                       QgsFeature,
                       QgsPoint,
                       QgsGeometry,
                       QgsWkbTypes,
                       QgsVectorLayer,
                       QgsVectorFileWriter,
                       QgsCoordinateReferenceSystem)

from photo2shape.backends import backendsRegistry

pluginPath = os.path.dirname(__file__)


class PhotoImporterTask(QgsTask):

    importComplete = pyqtSignal(str, bool)
    errorOccurred = pyqtSignal(str)

    def __init__(self, photos, fileName, encoding, backend, recurse, append, addToCanvas):
        QgsTask.__init__(self, 'Photo2Shape {}'.format(photos))

        self.photos = photos
        self.fileName = fileName
        self.encoding = encoding
        self.recurse = recurse
        self.append = append
        self.addToCanvas = addToCanvas

        self.backend = backendsRegistry[backend]

        self.error = ''

    def run(self):
        if self.append:
            layer = self._openShapefile()
        else:
            layer = self._newShapefile()

        if layer is None:
            self.error = self.tr('Unable to open or create layer.')
            return False

        provider = layer.dataProvider()
        fields = layer.fields()

        photos = []
        for root, dirs, files in os.walk(self.photos):
            if self.isCanceled():
                break

            photos.extend(os.path.join(root, fName) for fName in files if fName.lower().endswith(('.jpg', '.jpeg')))
            if not self.recurse:
                break

        if len(photos) == 0:
            self.error = self.tr('No images found in the directory.')
            return False

        ft = QgsFeature()
        ft.setFields(fields)

        total = 100.0 / len(photos)

        for count, fName in enumerate(photos):
            if self.isCanceled():
                break

            info, msg = self.backend.processFile(fName)
            if info is None:
                QgsMessageLog.logMessage(self.tr('Skipping file {fileName}: {error}'.format(fileName=fName, error=msg)), 'Photo2Shape', Qgis.Info)
                self.setProgress(int(count * total))
                continue

            # Write feature to layer
            altitude = info['altitude'] if info['altitude'] is not None else 0.0
            ft.setGeometry(QgsGeometry(QgsPoint(info['longitude'], info['latitude'], altitude)))
            ft['filepath'] = fName
            ft['longitude'] = info['longitude']
            ft['latitude'] = info['latitude']
            ft['altitude'] = info['altitude']
            ft['north'] = info['north']
            ft['azimuth'] = info['azimuth']
            ft['gps_date'] = info['gpsDate']
            ft['img_date'] = info['imgDate']
            provider.addFeatures([ft])

            self.setProgress(int(count * total))

        # copy style if it does not exists
        styleFile = '{}.qml'.format(os.path.splitext(self.fileName)[0])
        if not os.path.exists(styleFile):
            shutil.copy2(os.path.join(pluginPath, 'resources', 'photos.qml'), styleFile)

        return True

    def finished(self, result):
        if result:
            self.importComplete.emit(self.fileName, self.addToCanvas)
        else:
            self.errorOccurred.emit(self.error)

    def tr(self, text):
        return QCoreApplication.translate('PhotoImporterTask', text)

    def _openShapefile(self):
        layer = QgsVectorLayer(self.fileName, 'photo2shape', 'ogr')

        wkbType = layer.wkbType()
        if wkbType != QgsWkbTypes.PointZ:
            self.error = self.tr('File has incorrect WKB type "{}". Please select layer '
                                 'with "PointZ" WKB type.'.format(QgsWkbTypes.displayString(wkbType)))
            return None

        return layer

    def _newShapefile(self):
        fields = QgsFields()
        fields.append(QgsField('filepath', QVariant.String, '', 254))
        fields.append(QgsField('longitude', QVariant.Double, '', 20, 7))
        fields.append(QgsField('latitude', QVariant.Double, '', 20, 7))
        fields.append(QgsField('altitude', QVariant.Double, '', 20, 7))
        fields.append(QgsField('north', QVariant.String, '', 1))
        fields.append(QgsField('azimuth', QVariant.Double, '', 20, 7))
        fields.append(QgsField('gps_date', QVariant.String, '', 254))
        fields.append(QgsField('img_date', QVariant.String, '', 254))

        crs = QgsCoordinateReferenceSystem(4326)
        writer = QgsVectorFileWriter(self.fileName, self.encoding, fields, QgsWkbTypes.PointZ, crs, driverName='ESRI Shapefile')
        del writer

        layer = QgsVectorLayer(self.fileName, 'photo2shape', 'ogr')
        return layer
