# -*- coding: utf-8 -*-
#******************************************************************************
#
# demo
# ---------------------------------------------------------
# This plugin convert lesis GIS working dir structure to sqlite data base
#
# Author:   Alexander Lisovenko, alexander.lisovenko@nextgis.ru
# *****************************************************************************
# Copyright (c) 2015-2016. NextGIS, info@nextgis.com
#
# This source is free software; you can redistribute it and/or modify it under
# the terms of the GNU General Public License as published by the Free
# Software Foundation, either version 2 of the License, or (at your option)
# any later version.
#
# This code is distributed in the hope that it will be useful, but WITHOUT ANY
# WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
# details.
#
# A copy of the GNU General Public License is available on the World Wide Web
# at <http://www.gnu.org/licenses/>. You can also obtain it by writing
# to the Free Software Foundation, 51 Franklin Street, Suite 500 Boston,
# MA 02110-1335 USA.
#
#******************************************************************************
from PyQt4 import QtCore

from qgis.core import (
    QgsField,
    QgsFeatureRequest
)

from qgis_plugin_base import Plugin


class Worker(QtCore.QObject):

    started = QtCore.pyqtSignal()
    stoped = QtCore.pyqtSignal()
    progressChanged = QtCore.pyqtSignal(int, int)
    error = QtCore.pyqtSignal(unicode)

    def __init__(self, qgsVectorLayerPoint, qgsVectorLayerPolygon, filedName):
        QtCore.QObject.__init__(self)

        Plugin().plPrint("Worker __init__")

        self.qgsVectorLayerPoint = qgsVectorLayerPoint
        self.qgsVectorLayerPolygon = qgsVectorLayerPolygon
        self.filedName = filedName

    def addNewIntField(self):
        provider = self.qgsVectorLayerPolygon.dataProvider()
        self.qgsVectorLayerPolygon.startEditing()

        addingResult = provider.addAttributes([
            QgsField(self.filedName, QtCore.QVariant.Int)
        ])
        Plugin().plPrint("addingResult: %s" % addingResult)

        self.qgsVectorLayerPolygon.commitChanges()

    def run(self):
        self.started.emit()

        if self.qgsVectorLayerPoint is None:
            self.error.emit(self.tr("Point Layer not selected"))
            self.stoped.emit()
            return

        if self.qgsVectorLayerPolygon is None:
            self.error.emit(self.tr("Polygon Layer not selected"))
            self.stoped.emit()
            return

        provider = self.qgsVectorLayerPolygon.dataProvider()
        Plugin().plPrint("provider: %s" % provider)
        Plugin().plPrint("provider.capabilities(): %s" % provider.capabilities())
        Plugin().plPrint("provider.capabilitiesString(): %s" % provider.capabilitiesString())

        if self.filedName not in [f.name() for f in provider.fields().toList()]:
            self.addNewIntField()

        featureCount = self.qgsVectorLayerPolygon.featureCount()
        featureCounter = 0

        self.qgsVectorLayerPolygon.startEditing()

        self.progressChanged.emit(featureCounter, featureCount)
        try:
            for polygonLayerFeature in self.qgsVectorLayerPolygon.getFeatures():
                # Plugin().plPrint(str(polygonLayerFeature))
                polygonGeom = polygonLayerFeature.geometry()
                # Plugin().plPrint("bbox: %s" % polygonGeom.boundingBox())

                request = QgsFeatureRequest(
                    polygonGeom.boundingBox()
                )
                pcount = 0
                for pointLayerFeature in self.qgsVectorLayerPoint.getFeatures(request):
                    pointGeom = pointLayerFeature.geometry()

                    if (pointGeom is None):
                        continue

                    if pointGeom.within(polygonGeom):
                        pcount += 1

                # Plugin().plPrint("pcount: %d" % pcount)

                if pcount != 0:
                    polygonLayerFeature.setAttribute(
                        self.filedName,
                        pcount
                    )

                self.qgsVectorLayerPolygon.updateFeature(polygonLayerFeature)

                featureCounter += 1
                # Plugin().plPrint("Process %d polygones from %d" % (featureCounter, featureCount))
                self.progressChanged.emit(featureCounter, featureCount)

            self.qgsVectorLayerPolygon.commitChanges()
        except Exception as e:
            raise e
            self.qgsVectorLayerPolygon.rollBack()

        self.stoped.emit()
