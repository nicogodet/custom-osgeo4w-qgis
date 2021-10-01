# -*- coding: utf-8 -*-
"""
/***************************************************************************
 PointProjection
                                 A QGIS plugin
 test
                             -------------------
        begin                : 2016-03-16
        copyright            : (C) 2016 by toto
        email                : toto@toto
        git sha              : $Format:%H$
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
 This script initializes the plugin, making it known to QGIS.
"""


# noinspection PyPep8Naming
def classFactory(iface):  # pylint: disable=invalid-name
    """Load PointProjection class from file PointProjection.

    :param iface: A QGIS interface instance.
    :type iface: QgsInterface
    """
    #
    from .pointprojection import PointProjection

    return PointProjection(iface)
