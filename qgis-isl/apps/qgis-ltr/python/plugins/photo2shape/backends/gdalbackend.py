# -*- coding: utf-8 -*-

"""
***************************************************************************
    gdalbackend.py
    ---------------------
    Date                 : July 2018
    Copyright            : (C) 2018 by Alexander Bruy
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
__date__ = 'July 2018'
__copyright__ = '(C) 2018, Alexander Bruy'

# This will get replaced with a git SHA1 when you do a git archive

__revision__ = '$Format:%H$'

import re

from osgeo import gdal

from photo2shape.backends.backendbase import BackendBase


class GdalBackend(BackendBase):

    REGEX_COORD = re.compile(r'\(\s*([-\.\d]+)\s*\)\s*\(\s*([-\.\d]+)\s*\)\s*\(\s*([-\.\d]+)\)')
    REGEX_DATE = re.compile(r'\(([\d]+)\)\s*\(([\d]+)\)\s*\(([\d]+)\)')

    def name(self):
        return 'gdal'

    def displayName(self):
        return 'GDAL'

    def processFile(self, fileName):
        msg = ''
        gpsInfo = dict()

        ds = gdal.Open(fileName, gdal.GA_ReadOnly)
        if ds is None:
            msg = self.tr('Failed to open file.')
            return None, msg

        tags = ds.GetMetadata()
        ds = None

        # Start processing tags
        if not tags.keys() & {'EXIF_GPSLongitude', 'EXIF_GPSLatitude'}:
            msg = self.tr('There are no GPS tags in the file.')
            return None, msg

        gpsInfo['longitude'], gpsInfo['latitude'] = self._extractCoordinates(tags)
        if gpsInfo['longitude'] is None:
            msg = self.tr('There are no GPS fix data.')
            return None, msg

        altitude = self._extractAltitude(tags)
        gpsInfo['altitude'] = altitude if altitude is not None else 0.0
        gpsInfo['north'], gpsInfo['azimuth'] = self._extractDirection(tags)
        gpsInfo['gpsDate'] = self._extracrGPSDateTime(tags)
        gpsInfo['imgDate'] = self._extractImageDateTime(tags)

        return gpsInfo, msg

    def _extractCoordinates(self, tags):
        # Some devices (e.g. with Android 1.6) write tags in non standard
        # way as decimal degrees in ASCII field
        if '(' not in tags['EXIF_GPSLongitude']:
            lon = round(float(tags['EXIF_GPSLongitude']), 7)
            lat = round(float(tags['EXIF_GPSLatitude']), 7)
            return lon, lat

        # Sometimes tags present but filled with zeros
        if tags['EXIF_GPSLongitude'].strip() == '(0) (0) (0)':
            return None, None

        # Longitude direction will be either 'E' or 'W'
        lonDirection = tags['EXIF_GPSLongitudeRef']
        m = self.REGEX_COORD.search(tags['EXIF_GPSLongitude'].strip())
        if m is not None:
            dd = float(m.group(1))
            mm = float(m.group(2)) / 60.0
            ss = float(m.group(3)) / 3600.0
            lon = round(dd + mm + ss, 7)

        # Latitude direction will be either 'N' or 'S'
        latDirection = tags['EXIF_GPSLatitudeRef']
        # Coordinates stored as list of degrees, minutes and seconds
        m = self.REGEX_COORD.search(tags['EXIF_GPSLatitude'].strip())
        if m is not None:
            dd = float(m.group(1))
            mm = float(m.group(2)) / 60.0
            ss = float(m.group(3)) / 3600.0
            lat = round(dd + mm + ss, 7)

        # Apply direction
        if lonDirection == 'W':
            lon = -lon
        if latDirection == 'S':
            lat = -lat

        return lon, lat

    def _extractAltitude(self, tags):
        if 'EXIF_GPSAltitude' not in tags:
            return None

        # Some devices (e.g. with Android 1.6) write tags in non standard
        # way as ASCII field. Also they don't write GPS GPSAltitudeRef tag
        if '(' not in tags['EXIF_GPSAltitude']:
            return round(float(tags['EXIF_GPSAltitude']), 7)

        if 'EXIF_GPSAltitudeRef' not in tags:
            return None

        altitude = round(float(tags['EXIF_GPSAltitude'].strip('()')), 7)

        # Reference will be either 0 or 1
        if '1' in tags['EXIF_GPSAltitudeRef']:
            altitude = -altitude

        return altitude

    def _extractDirection(self, tags):
        if 'EXIF_GPSImgDirection' not in tags:
            return None, None

        # Sometimes tag present by filled with zeros
        if tags['EXIF_GPSImgDirection'] == '(0)':
            return None, None

        # Reference will be either 'T' or 'M'
        reference = tags['EXIF_GPSImgDirectionRef']

        azimuth = round(float(tags['EXIF_GPSImgDirection'].strip('()')), 7)

        return reference, azimuth

    def _extracrGPSDateTime(self, tags):
        imgDate = None
        if 'EXIF_GPSDateStamp' in tags:
            imgDate = tags['EXIF_GPSDateStamp']

        if 'EXIF_GPSTimeStamp' in tags:
            # Some devices (e.g. with Android 1.6) write tags in non standard
            # way as ASCII field. Also they don't write GPS GPSDate tag
            if '(' not in tags['EXIF_GPSTimeStamp']:
                return tags['EXIF_GPSTimeStamp']
            else:
                m = self.REGEX_DATE.search(tags['EXIF_GPSTimeStamp'].strip())
                if m is not None:
                    imgTime = '{:0>2}:{:0>2}:{:0>2}'.format(m.group(1), m.group(2), m.group(3))

                    if imgDate is None:
                        return imgTime
                    else:
                        return '{} {}'.format(imgDate, imgTime)

        return None

    def _extractImageDateTime(self, tags):
        if 'EXIF_DateTime' in tags:
            return tags['EXIF_DateTime']

        return None
