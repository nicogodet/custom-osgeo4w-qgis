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


# import qgis
from qgis.core import (
    QgsWkbTypes,
    QgsGeometry,
    QgsPointXY,
    QgsFeatureRequest,
    QgsCoordinateTransform,
    QgsProject,
)
from qgis.utils import iface

# import numpy
import numpy as np

# imports divers
import math
from shapely.geometry import *


class pointProjector:
    def __init__(self, pointlayer, interpfield=-1, linecrs=None, rubberband=None):
        """
        constructor
        """
        self.pointLayer = pointlayer  # the point layer that will be projected
        self.interpField = interpfield  # The index of field of point layer that will be interpolated
        self.projectedPoints = []  # The projected points numpy array
        self.bufferGeom = None  # The geom of the buffer
        self.rubberband = rubberband  # the rubberband
        if linecrs != None:  # The crs of the line layer
            self.lineCrs = linecrs
        else:
            self.lineCrs = self.pointLayer.crs()

    def computeProjectedPoints(self, line, options):
        """
        compute the projected points
        return :
            self.bufferGeom : the qgsgeometry of the buffer
            self.projectedPoints : [..., [(point caracteristics : )
                                          #index : descripion
                                          #0 : the pk of the projected point relative to line
                                          #1 : the x coordinate of the projected point
                                          #2 : the y coordinate of the projected point
                                          #3 : the lenght between original point and projected point else -1 if interpolated
                                          #4 : the segment of the polyline on which the point is projected
                                          #5 : the interp value if interpfield>-1, else None
                                          #6 : the x coordinate of the original point if the point is not interpolated, else None
                                          #6 : the y coordinate of the original point if the point is not interpolated, else None
                                          #6 : the feature the original point if the point is not interpolated, else None],
                                           ...]
        """
        self.projectedPoints = []
        self.bufferGeom = None
        line = self.changeFetLineCrs(line)
        lineGeom = line.geometry()

        if lineGeom.isMultipart():
            line = LineString(lineGeom.asMultiPolyline()[0])
        else:
            line = LineString(lineGeom.asPolyline())

        # Select points in buffer
        if self.pointLayer != None:
            self.bufferGeom = lineGeom.buffer(options["buffer"], 10)
            requestedFeatures = self.pointLayer.getFeatures(
                QgsFeatureRequest().setFilterRect(self.bufferGeom.boundingBox())
            )
            for feature in requestedFeatures:
                featureGeom = feature.geometry()
                # iterate preselected point features and perform exact check with current polygon
                if featureGeom.intersects(self.bufferGeom):
                    if featureGeom.isMultipart():
                        point = Point(featureGeom.asMultiPoint()[0].x(), featureGeom.asMultiPoint()[0].y())
                    else:
                        point = Point(featureGeom.asPoint().x(), featureGeom.asPoint().y())

                    point2, dist1, lenght, segment = self.Closest_point(line, point)

                    if self.interpField > -1:
                        interptemp = float(feature[self.interpField])
                    else:
                        interptemp = None

                    self.projectedPoints.append(
                        [
                            lenght,
                            point2.x,
                            point2.y,
                            dist1,
                            segment,
                            interptemp,
                            point.x,
                            point.y,
                            feature,
                        ]
                    )
        self.projectedPoints = np.array(self.projectedPoints)
        # perform postprocess computation
        if len(self.projectedPoints) > 0:
            if options["delDupPoints"]:
                # Remove duplicate points
                self.removeDuplicateLenght()
            if options["spatialstep"] > 0:
                # Interpolate points between projected points TEST HERE
                self.interpolateNodeofPolyline(lineGeom)
                # discretize points
                self.discretizeLine(options["spatialstep"])
            return self.bufferGeom, self.projectedPoints
        else:
            return self.bufferGeom, None

    def discretizeLine(self, spatialstep):
        """
        discretize self.projectedPoints
        """
        tempprojected = []
        for i, projectedpoint in enumerate(self.projectedPoints):
            if i == len(self.projectedPoints) - 1:
                break
            else:
                long = self.projectedPoints[i + 1][0] - self.projectedPoints[i][0]
                if long > spatialstep:
                    count = int(long / spatialstep)
                    for j in range(1, count + 1):
                        interpx = self.projectedPoints[i][1] + (
                            self.projectedPoints[i + 1][1] - self.projectedPoints[i][1]
                        ) / long * (spatialstep * j)
                        interpy = self.projectedPoints[i][2] + (
                            self.projectedPoints[i + 1][2] - self.projectedPoints[i][2]
                        ) / long * (spatialstep * j)
                        if self.interpField > -1:
                            interpz = self.projectedPoints[i][5] + (
                                self.projectedPoints[i + 1][5] - self.projectedPoints[i][5]
                            ) / long * (spatialstep * j)
                        else:
                            interpz = None
                        tempprojected.append(
                            [
                                self.projectedPoints[i][0] + j * spatialstep,
                                interpx,
                                interpy,
                                -1,
                                self.projectedPoints[i][4],
                                interpz,
                                None,
                                None,
                                None,
                            ]
                        )
        self.projectedPoints = np.append(self.projectedPoints, tempprojected, axis=0)
        self.projectedPoints = self.projectedPoints[self.projectedPoints[:, 0].argsort()]

    def removeDuplicateLenght(self):
        """
        remove points with same pk of self.projectedPoints
        """
        workArray = self.projectedPoints[:, 0].tolist()
        duplicatevalues = set([x for x in workArray if workArray.count(x) > 1])
        while len(duplicatevalues) > 0:
            for i, duplicatevaluetemp in enumerate(duplicatevalues):
                if i == 0:
                    duplicatevalue = duplicatevaluetemp
                    break
            equalsvalueindex = np.where(np.array(workArray) == duplicatevalue)
            nearestelem = self.projectedPoints[equalsvalueindex[0]][0]
            for elem in self.projectedPoints[equalsvalueindex]:
                if elem[3] < nearestelem[3]:
                    nearestelem = elem
            self.projectedPoints = np.delete(self.projectedPoints, equalsvalueindex, axis=0)
            self.projectedPoints = np.append(self.projectedPoints, [nearestelem], axis=0)

            workArray = self.projectedPoints[:, 0].tolist()
            duplicatevalues = set([x for x in workArray if workArray.count(x) > 1])
        self.projectedPoints = self.projectedPoints[self.projectedPoints[:, 0].argsort()]

    def interpolateNodeofPolyline(self, geom):
        """
        add points to self.projectedPoints for the nodes of the line
        """
        try:
            polyline = geom.asPolyline()
        except TypeError:
            polyline = geom.asMultiPolyline()[0]
        self.projectedPoints = self.projectedPoints[self.projectedPoints[:, 0].argsort()]
        lenpoly = 0
        # Write fist and last element
        if self.projectedPoints[0][0] != 0:
            self.projectedPoints = np.append(
                self.projectedPoints,
                [
                    [
                        0,
                        polyline[0].x(),
                        polyline[0].y(),
                        -1,
                        0,
                        self.projectedPoints[0][5],
                        polyline[0].x(),
                        polyline[0].y(),
                        self.projectedPoints[0][8],
                    ]
                ],
                axis=0,
            )
            self.projectedPoints = self.projectedPoints[self.projectedPoints[:, 0].argsort()]
        if self.projectedPoints[-1][0] != geom.length():
            self.projectedPoints = np.append(
                self.projectedPoints,
                [
                    [
                        geom.length(),
                        polyline[-1].x(),
                        polyline[-1].y(),
                        -1,
                        len(polyline) - 2,
                        self.projectedPoints[-1][5],
                        polyline[-1].x(),
                        polyline[-1].y(),
                        self.projectedPoints[0][8],
                    ]
                ],
                axis=0,
            )
            self.projectedPoints = self.projectedPoints[self.projectedPoints[:, 0].argsort()]
        # Compute points inside the line
        for i, point in enumerate(polyline):
            if i == 0:
                continue
            elif i == len(polyline) - 1:
                break
            else:
                lenpoly += (
                    (polyline[i].x() - polyline[i - 1].x()) ** 2 + (polyline[i].y() - polyline[i - 1].y()) ** 2
                ) ** 0.5
                # search if a point exist on the node - if true skip :
                if len(np.where(self.projectedPoints[:, 0] == lenpoly)[0]) > 0:
                    continue
                else:
                    # find previous and next real point index
                    previouspointindex = np.max(np.where(self.projectedPoints[:, 0] <= lenpoly)[0])
                    segmentmin = int(self.projectedPoints[previouspointindex][4])
                    nextpointindex = np.min(np.where(self.projectedPoints[:, 0] >= lenpoly)[0])
                    segmentmax = int(self.projectedPoints[nextpointindex][4])
                    # find total lenght between two real points
                    lentot = (
                        (polyline[segmentmin + 1].x() - self.projectedPoints[previouspointindex][1]) ** 2
                        + (polyline[segmentmin + 1].y() - self.projectedPoints[previouspointindex][2]) ** 2
                    ) ** 0.5
                    lentemp = lentot
                    for j in range(segmentmin + 1, segmentmax):
                        if j == i:
                            lentemp = lentot
                        lentot += (
                            (polyline[j + 1].x() - polyline[j].x()) ** 2 + (polyline[j + 1].y() - polyline[j].y()) ** 2
                        ) ** 0.5
                    lentot += (
                        (self.projectedPoints[nextpointindex][1] - polyline[segmentmax].x()) ** 2
                        + (self.projectedPoints[nextpointindex][2] - polyline[segmentmax].y()) ** 2
                    ) ** 0.5
                    # "interpolate"
                    if self.interpField > -1:
                        z = (
                            self.projectedPoints[previouspointindex][5]
                            + (self.projectedPoints[nextpointindex][5] - self.projectedPoints[previouspointindex][5])
                            / lentot
                            * lentemp
                        )
                    else:
                        z = None
                    self.projectedPoints = np.append(
                        self.projectedPoints,
                        [
                            [
                                lenpoly,
                                point.x(),
                                point.y(),
                                -1,
                                i,
                                z,
                                polyline[i].x(),
                                polyline[i].y(),
                                None,
                            ]
                        ],
                        axis=0,
                    )
                    self.projectedPoints = self.projectedPoints[self.projectedPoints[:, 0].argsort()]
        self.projectedPoints = self.projectedPoints[self.projectedPoints[:, 0].argsort()]

    def visualResultTestLine(self):
        """
        Draw result of the traitment of selected line with a rubberband
        """
        self.resetRubberband()
        if self.projectedPoints.all() != None:
            featuretoselect = [
                projectedpoint.id() for projectedpoint in self.projectedPoints[:, 8] if projectedpoint != None
            ]
            self.pointLayer.selectByIds(featuretoselect)
            self.drawProjectedPointsonRubberband()
        else:
            self.rubberband.reset(QgsWkbTypes.LineGeometry)

    def drawProjectedPointsonRubberband(self):
        xform = QgsCoordinateTransform(
            self.pointLayer.crs(),
            iface.mapCanvas().mapSettings().destinationCrs(),
            QgsProject.instance(),
        )
        if self.bufferGeom != None:
            xformbufferline = []
            bufferline = self.bufferGeom.convertToType(QgsWkbTypes.LineGeometry)
            for point in bufferline.asPolyline():
                xformbufferline.append(xform.transform(QgsPointXY(point[0], point[1])))
            self.rubberband.addGeometry(QgsGeometry.fromPolylineXY(xformbufferline), None)
        for point in self.projectedPoints:
            x1, y1 = point[1], point[2]
            x2, y2 = point[6], point[7]
            self.rubberband.addGeometry(
                QgsGeometry.fromPolylineXY(
                    [
                        xform.transform(QgsPointXY(x1, y1)),
                        xform.transform(QgsPointXY(x2, y2)),
                    ]
                ),
                None,
            )

    def createMatPlotLibGraph(self, canvas1, ax1):
        ax1.cla()
        if self.interpField > -1:
            ax1.grid(color="0.5", linestyle="-", linewidth=0.5)
            ax1.plot(
                self.projectedPoints[:, 0],
                self.projectedPoints[:, 5],
                linewidth=3,
                visible=True,
            )
            canvas1.draw()
        else:
            ax1.grid(color="0.5", linestyle="-", linewidth=0.5)
            canvas1.draw()

    def resetRubberband(self):
        try:
            self.rubberband.reset(QgsWkbTypes.LineGeometry)
        except Exception as e:
            pass
        self.pointLayer.removeSelection()

    def changeFetLineCrs(self, fetline):
        try:
            geom = fetline.geometry().asMultiPolyline()[0]
        except TypeError:
            geom = fetline.geometry().asPolyline()
        xform1 = QgsCoordinateTransform(self.lineCrs, self.pointLayer.crs(), QgsProject.instance())
        geomtransf = []
        for point in geom:
            geomtransf.append(xform1.transform(point))
        fetline.setGeometry(QgsGeometry.fromPolylineXY(geomtransf))
        return fetline

    # ***************** Core projection algorithm

    # these methods rewritten from the C version of Paul Bourke's
    # geometry computations:
    # http://local.wasp.uwa.edu.au/~pbourke/geometry/pointline/
    def magnitude(self, p1, p2):
        vect_x = p2.x - p1.x
        vect_y = p2.y - p1.y
        return math.sqrt(vect_x ** 2 + vect_y ** 2)

    def intersect_point_to_line(self, point, line_start, line_end):
        line_magnitude = self.magnitude(line_end, line_start)
        u = (
            (point.x - line_start.x) * (line_end.x - line_start.x)
            + (point.y - line_start.y) * (line_end.y - line_start.y)
        ) / (line_magnitude ** 2)

        # closest point does not fall within the line segment,
        # take the shorter distance to an endpoint
        if u < 0.00001 or u > 1:
            ix = self.magnitude(point, line_start)
            iy = self.magnitude(point, line_end)
            if ix > iy:
                return line_end
            else:
                return line_start
        else:
            ix = line_start.x + u * (line_end.x - line_start.x)
            iy = line_start.y + u * (line_end.y - line_start.y)
            return Point([ix, iy])

    def Closest_point(self, line, point):
        nearest_point = None
        min_dist = float("inf")
        lenght = []
        for i, coord in enumerate(line.coords):
            if i == len(line.coords) - 1:
                break
            line_start = Point(line.coords[i])
            line_end = Point(line.coords[i + 1])
            lenght.append(((line_start.x - line_end.x) ** 2 + (line_start.y - line_end.y) ** 2) ** 0.5)
            intersection_point = self.intersect_point_to_line(point, line_start, line_end)
            cur_dist = self.magnitude(point, intersection_point)
            if cur_dist < min_dist:
                min_dist = cur_dist
                nearest_point = intersection_point
                lenghtfrompreviouspoint = (
                    (line_start.x - nearest_point.x) ** 2 + (line_start.y - nearest_point.y) ** 2
                ) ** 0.5
                segmentmin = i
        lenghtfromstart = 0
        for j in range(segmentmin):
            lenghtfromstart += lenght[j]
        lenghtfromstart += lenghtfrompreviouspoint

        return (nearest_point, min_dist, lenghtfromstart, segmentmin)
