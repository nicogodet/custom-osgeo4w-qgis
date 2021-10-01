# -*- coding: utf-8 -*-

"""
***************************************************************************
    backendbase.py
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


from qgis.PyQt.QtCore import QCoreApplication


class BackendBase:

    def name(self):
        return 'base'

    def displayName(self):
        return 'Base backend'

    def tr(self, text):
        return QCoreApplication.translate(self.__class__.__name__, text)

    def processFile(self, fileName):
        raise NotImplementedError('Needs to be implemented by subclasses.')
